#!/usr/bin/env python3
"""
고급 RAG 시스템 - 하이브리드 검색 및 한국어 최적화
"""

import asyncio
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
import chromadb
from chromadb.config import Settings
import json
from datetime import datetime
import os
from dataclasses import asdict
from modules.data_processor import UnifiedProduct
from utils import get_logger

logger = get_logger(__name__)

class KoreanEmbeddingEngine:
    """한국어 최적화 임베딩 엔진"""
    
    def __init__(self, model_name: str = "jhgan/ko-sroberta-multitask"):
        self.model_name = model_name
        self.model = None
        self.device = "cpu"  # GPU 사용 시 "cuda"로 변경
        
    async def initialize(self):
        """임베딩 모델 초기화"""
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(self.model_name)
        self.model.to(self.device)
        logger.info(f"한국어 임베딩 모델 로드 완료: {self.model_name}")


    async def create_embeddings(self, texts: List[str]) -> np.ndarray:
        """텍스트 리스트를 벡터로 변환"""
        if not texts:
            return np.array([])
        
        if self.model is None:
            # Mock 임베딩 생성 (실제로는 sentence-transformers 사용)
            return self._generate_mock_embeddings(texts)
        
        embeddings = self.model.encode(
            texts,
            batch_size=32,
            show_progress_bar=False,
            convert_to_numpy=True
        )
        logger.info(f"{len(texts)}개 텍스트 임베딩 생성 완료")
        return embeddings

    
    def _generate_mock_embeddings(self, texts: List[str]) -> np.ndarray:
        """Mock 임베딩 생성 (개발/테스트용)"""
        # 텍스트 길이와 특성을 기반으로 단순한 벡터 생성
        embeddings = []
        for text in texts:
            # 텍스트 특성을 반영한 512차원 벡터 생성
            text_hash = hash(text) % 10000
            np.random.seed(text_hash)
            vector = np.random.normal(0, 1, 512)
            
            # 텍스트 길이 반영
            vector[0] = len(text) / 100.0
            
            # 한글 포함 여부 반영
            korean_chars = len([c for c in text if '가' <= c <= '힣'])
            vector[1] = korean_chars / len(text) if text else 0
            
            # 숫자 포함 여부 반영
            digit_chars = len([c for c in text if c.isdigit()])
            vector[2] = digit_chars / len(text) if text else 0
            
            # 정규화
            vector = vector / np.linalg.norm(vector)
            embeddings.append(vector)
        
        return np.array(embeddings)
    
    def create_product_embedding_text(self, product: UnifiedProduct) -> str:
        """상품 정보를 임베딩용 텍스트로 변환"""
        parts = [
            f"제품명: {product.name['normalized']}",
            f"카테고리: {' > '.join(product.category)}",
            f"가격: {product.price['amount']:,}원"
        ]
        
        # 주요 사양 추가
        for key, value in list(product.specifications.items())[:5]:
            if value and str(value).strip():
                parts.append(f"{key}: {value}")
        
        # 메타데이터에서 중요한 정보 추가
        if product.metadata.get('organization'):
            parts.append(f"기관: {product.metadata['organization']}")
        
        if product.metadata.get('vendor'):
            parts.append(f"판매자: {product.metadata['vendor']}")
        
        return " | ".join(parts)

class BM25Scorer:
    """BM25 키워드 검색 구현"""
    
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus = []
        self.tokenized_corpus = []
        self.doc_freqs = []
        self.idf = {}
        self.avgdl = 0.0
    
    def fit(self, corpus: List[str]):
        """코퍼스로 BM25 모델 학습"""
        self.corpus = corpus
        self.tokenized_corpus = [self._tokenize(doc) for doc in corpus]
        
        # 문서 길이 계산
        self.avgdl = sum(len(doc) for doc in self.tokenized_corpus) / len(self.tokenized_corpus)
        
        # 단어 빈도 계산
        self._calculate_doc_freqs()
        self._calculate_idf()
        
        logger.info(f"BM25 모델 학습 완료: {len(corpus)}개 문서")
    
    def get_scores(self, query: str) -> np.ndarray:
        """쿼리에 대한 BM25 점수 계산"""
        query_tokens = self._tokenize(query)
        scores = np.zeros(len(self.tokenized_corpus))
        
        for token in query_tokens:
            if token not in self.idf:
                continue
            
            idf_score = self.idf[token]
            for i, doc in enumerate(self.tokenized_corpus):
                tf = doc.count(token)
                dl = len(doc)
                
                score = idf_score * (tf * (self.k1 + 1)) / (
                    tf + self.k1 * (1 - self.b + self.b * dl / self.avgdl)
                )
                scores[i] += score
        
        return scores
    
    def _tokenize(self, text: str) -> List[str]:
        """텍스트 토큰화 (한국어 고려)"""
        import re
        
        # 한글, 영문, 숫자만 유지
        text = re.sub(r'[^\w가-힣]', ' ', text.lower())
        
        # 공백으로 분할
        tokens = text.split()
        
        # 한글의 경우 2-gram도 추가 (간단한 형태소 분석 대용)
        korean_tokens = []
        for token in tokens:
            if any('가' <= c <= '힣' for c in token) and len(token) >= 2:
                for i in range(len(token) - 1):
                    korean_tokens.append(token[i:i+2])
        
        return tokens + korean_tokens
    
    def _calculate_doc_freqs(self):
        """문서별 단어 빈도 계산"""
        self.doc_freqs = []
        for doc in self.tokenized_corpus:
            freq = {}
            for token in doc:
                freq[token] = freq.get(token, 0) + 1
            self.doc_freqs.append(freq)
    
    def _calculate_idf(self):
        """IDF 계산"""
        vocab = set()
        for doc in self.tokenized_corpus:
            vocab.update(doc)
        
        for token in vocab:
            df = sum(1 for doc in self.tokenized_corpus if token in doc)
            self.idf[token] = np.log((len(self.tokenized_corpus) - df + 0.5) / (df + 0.5))

class HybridSearchEngine:
    """하이브리드 검색 엔진 (의미적 + 키워드)"""
    
    def __init__(self):
        self.embedding_engine = KoreanEmbeddingEngine()
        self.bm25 = BM25Scorer()
        self.products = []
        self.embeddings = None
        self.is_initialized = False
    
    async def initialize(self):
        """검색 엔진 초기화"""
        await self.embedding_engine.initialize()
        self.is_initialized = True
        logger.info("하이브리드 검색 엔진 초기화 완료")
    
    async def index_products(self, products: List[UnifiedProduct]):
        """상품 인덱싱"""
        if not self.is_initialized:
            await self.initialize()
        
        logger.info(f"상품 인덱싱 시작: {len(products)}개")
        
        self.products = products
        
        # 임베딩용 텍스트 생성
        embedding_texts = [
            self.embedding_engine.create_product_embedding_text(product)
            for product in products
        ]
        
        # 의미적 검색을 위한 임베딩 생성
        self.embeddings = await self.embedding_engine.create_embeddings(embedding_texts)
        
        # BM25를 위한 키워드 검색 인덱싱
        bm25_texts = [
            f"{product.name['searchable']} {' '.join(product.category)} {product.specifications}"
            for product in products
        ]
        self.bm25.fit(bm25_texts)
        
        logger.info(f"상품 인덱싱 완료: {len(products)}개")
    
    async def search(self, query: str, k: int = 10, alpha: float = 0.6) -> List[Dict]:
        """하이브리드 검색 실행"""
        if not self.products or self.embeddings is None:
            logger.warning("인덱싱된 상품이 없음")
            return []
        
        logger.info(f"하이브리드 검색 실행: '{query}'")
        
        # 1. 의미적 검색
        query_embedding = await self.embedding_engine.create_embeddings([query])
        if query_embedding.size > 0:
            semantic_scores = np.dot(self.embeddings, query_embedding.T).flatten()
        else:
            semantic_scores = np.zeros(len(self.products))
        
        # 2. 키워드 검색
        bm25_scores = self.bm25.get_scores(query)
        
        # 3. 점수 정규화
        semantic_scores_norm = self._normalize_scores(semantic_scores)
        bm25_scores_norm = self._normalize_scores(bm25_scores)
        
        # 4. 하이브리드 점수 계산
        hybrid_scores = alpha * semantic_scores_norm + (1 - alpha) * bm25_scores_norm
        
        # 5. 상위 k개 결과 선택
        top_indices = np.argsort(hybrid_scores)[::-1][:k]
        
        results = []
        for idx in top_indices:
            if hybrid_scores[idx] > 0:  # 점수가 0보다 큰 경우만
                results.append({
                    'product': self.products[idx],
                    'score': float(hybrid_scores[idx]),
                    'semantic_score': float(semantic_scores_norm[idx]),
                    'keyword_score': float(bm25_scores_norm[idx]),
                    'rank': len(results) + 1
                })
        
        logger.info(f"검색 완료: {len(results)}개 결과")
        return results
    
    def _normalize_scores(self, scores: np.ndarray) -> np.ndarray:
        """점수 정규화 (0-1 범위)"""
        if scores.max() == scores.min():
            return np.zeros_like(scores)
        return (scores - scores.min()) / (scores.max() - scores.min())

class AdvancedVectorDbModule:
    """고급 벡터 DB 모듈"""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        self.client = None
        self.collection = None
        self.hybrid_search = HybridSearchEngine()
    
    async def initialize(self):
        """벡터 DB 초기화"""
        try:
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # 컬렉션 생성 또는 가져오기
            try:
                self.collection = self.client.get_collection("procurement_products")
                logger.info("기존 벡터 DB 컬렉션 로드")
            except:
                self.collection = self.client.create_collection(
                    name="procurement_products",
                    metadata={"description": "조달 상품 정보"}
                )
                logger.info("새 벡터 DB 컬렉션 생성")
            
            # 하이브리드 검색 엔진 초기화
            await self.hybrid_search.initialize()
            
            logger.info("고급 벡터 DB 모듈 초기화 완료")
            
        except Exception as e:
            logger.error(f"벡터 DB 초기화 실패: {str(e)}", exc_info=True)
            raise
    
    async def add_products(self, products: List[UnifiedProduct]):
        """상품 벡터 DB에 추가"""
        if not products:
            return
        
        logger.info(f"벡터 DB에 상품 추가: {len(products)}개")
        
        # 하이브리드 검색 엔진에 인덱싱
        await self.hybrid_search.index_products(products)
        
        # ChromaDB에 저장
        documents = []
        metadatas = []
        ids = []
        
        for product in products:
            # 문서 텍스트 생성
            doc_text = self.hybrid_search.embedding_engine.create_product_embedding_text(product)
            documents.append(doc_text)
            
            # 메타데이터 준비
            metadata = {
                'source': product.source,
                'category': '/'.join(product.category),
                'price': float(product.price['amount']),
                'name': product.name['normalized'],
                'created_at': datetime.now().isoformat()
            }
            
            # ChromaDB 메타데이터 제한 (문자열, 숫자, 불린만)
            for key, value in product.metadata.items():
                if isinstance(value, (str, int, float, bool)):
                    metadata[f'meta_{key}'] = value
            
            metadatas.append(metadata)
            ids.append(product.id)
        
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        logger.info(f"벡터 DB 저장 완료: {len(products)}개")


    async def search_similar_products(self, query: str, limit: int = 5) -> List[Dict]:
        """유사 상품 검색"""
        # 하이브리드 검색 실행
        hybrid_results = await self.hybrid_search.search(query, k=limit)
        
        # ChromaDB 검색도 수행 (백업)
        chroma_results = []
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=limit
            )
            
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    chroma_results.append({
                        'document': doc,
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i] if results['distances'] else 0.5
                    })
        except Exception as e:
            logger.warning(f"ChromaDB 검색 실패: {str(e)}")
        
        # 하이브리드 결과를 우선 사용
        if hybrid_results:
            formatted_results = []
            for result in hybrid_results:
                product = result['product']
                formatted_results.append({
                    'document': self.hybrid_search.embedding_engine.create_product_embedding_text(product),
                    'metadata': {
                        'source': product.source,
                        'name': product.name['normalized'],
                        'price': float(product.price['amount']),
                        'category': '/'.join(product.category)
                    },
                    'distance': 1.0 - result['score'],  # 점수를 거리로 변환
                    'hybrid_score': result['score'],
                    'semantic_score': result['semantic_score'],
                    'keyword_score': result['keyword_score']
                })
            
            logger.info(f"하이브리드 검색 결과: {len(formatted_results)}개")
            return formatted_results
        
        # 하이브리드 결과가 없으면 ChromaDB 결과 사용
        logger.info(f"ChromaDB 검색 결과: {len(chroma_results)}개")
        return chroma_results
        

    
    async def find_similar_procurement_cases(self, analysis: Dict, limit: int = 3) -> List[Dict]:
        """유사한 조달 사례 검색"""

        # 분석 결과를 쿼리 텍스트로 변환
        query_parts = []
        
        if analysis.get('items'):
            query_parts.append(f"제품: {', '.join(analysis['items'])}")
        
        if analysis.get('budget_range'):
            query_parts.append(f"예산: {analysis['budget_range']}")
        
        if analysis.get('urgency'):
            query_parts.append(f"긴급도: {analysis['urgency']}")
        
        query = " | ".join(query_parts)
        
        # G2B 데이터만 필터링하여 검색
        results = await self.search_similar_products(query, limit * 2)
        
        # G2B 조달 사례만 필터링
        procurement_cases = []
        for result in results:
            if result.get('metadata', {}).get('source') == 'g2b':
                procurement_cases.append(result)
                if len(procurement_cases) >= limit:
                    break
        
        logger.info(f"유사 조달 사례 검색 완료: {len(procurement_cases)}개")
        return procurement_cases
        

    
    async def get_statistics(self) -> Dict:
        """벡터 DB 통계 정보"""
        count = self.collection.count()
        
        return {
            'total_products': count,
            'collection_name': self.collection.name,
            'hybrid_search_ready': len(self.hybrid_search.products) > 0,
            'last_updated': datetime.now().isoformat()
        }


# 사용 예시
async def test_advanced_rag():
    """고급 RAG 시스템 테스트"""
    # 벡터 DB 초기화
    rag_module = AdvancedVectorDbModule()
    await rag_module.initialize()
    
    # 테스트 상품 데이터
    from modules.data_processor import UnifiedProduct
    from decimal import Decimal
    
    test_products = [
        UnifiedProduct(
            id="test_1",
            source="g2b",
            name={
                "original": "사무용 책상 구매",
                "normalized": "사무용 책상",
                "searchable": "사무용 책상"
            },
            price={
                "amount": Decimal("450000"),
                "currency": "KRW",
                "vat_included": True
            },
            category=["사무용품", "가구", "책상"],
            specifications={"크기": "1800x800mm", "재질": "MDF"},
            metadata={"organization": "테스트 기관"},
            timestamps={"created": datetime.now()}
        )
    ]
    
    # 상품 추가
    await rag_module.add_products(test_products)
    
    # 검색 테스트
    results = await rag_module.search_similar_products("사무용 책상", 5)
    print(f"검색 결과: {len(results)}개")
    
    for result in results:
        print(f"- {result.get('metadata', {}).get('name', 'Unknown')}")
    
    # 통계 확인
    stats = await rag_module.get_statistics()
    print(f"벡터 DB 통계: {stats}")

if __name__ == "__main__":
    asyncio.run(test_advanced_rag())
