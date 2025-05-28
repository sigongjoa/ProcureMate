#!/usr/bin/env python3

import pytest
import asyncio
import sys
from pathlib import Path
import numpy as np

sys.path.append(str(Path(__file__).parent.parent))
from modules.advanced_rag_module import KoreanEmbeddingEngine, BM25Scorer, HybridSearchEngine, AdvancedRAGModule
from modules.data_processor import UnifiedProduct
from decimal import Decimal

class TestAdvancedRAG:
    
    @pytest.fixture
    def embedding_engine(self):
        return KoreanEmbeddingEngine()
    
    @pytest.fixture
    def bm25_scorer(self):
        return BM25Scorer()
    
    @pytest.fixture
    def sample_products(self):
        return [
            UnifiedProduct(
                id="p1", source="test",
                name={"original": "사무용 의자", "normalized": "사무용 의자"},
                price={"amount": Decimal("100000"), "currency": "KRW"},
                category=["사무용품", "의자"],
                specifications={"색상": "검정", "재질": "가죽"}
            ),
            UnifiedProduct(
                id="p2", source="test",
                name={"original": "컴퓨터 책상", "normalized": "컴퓨터 책상"},
                price={"amount": Decimal("200000"), "currency": "KRW"},
                category=["사무용품", "책상"],
                specifications={"크기": "120x60cm", "재질": "목재"}
            ),
            UnifiedProduct(
                id="p3", source="test", 
                name={"original": "무선 마우스", "normalized": "무선 마우스"},
                price={"amount": Decimal("30000"), "currency": "KRW"},
                category=["전자제품", "마우스"],
                specifications={"연결": "무선", "배터리": "AA"}
            )
        ]
    
    def test_korean_embedding_engine_init(self, embedding_engine):
        try:
            assert embedding_engine.model is not None
            assert embedding_engine.device is not None
            print("DEBUG: 한국어 임베딩 엔진 초기화 성공")
        except Exception as e:
            print(f"ERROR: {str(e)}")
            raise
    
    def test_create_product_embeddings(self, embedding_engine, sample_products):
        try:
            embeddings = embedding_engine.create_product_embeddings(sample_products)
            
            assert isinstance(embeddings, np.ndarray)
            assert embeddings.shape[0] == len(sample_products)
            assert embeddings.shape[1] > 0  # 임베딩 차원이 0보다 큰지
            
            print(f"DEBUG: 임베딩 생성 완료 - 형태: {embeddings.shape}")
        except Exception as e:
            print(f"ERROR: {str(e)}")
            raise
    
    def test_bm25_scoring(self, bm25_scorer, sample_products):
        try:
            # BM25 인덱스 구축
            bm25_scorer.build_index(sample_products)
            
            # 검색 수행
            query = "사무용 의자"
            scores = bm25_scorer.search(query, top_k=3)
            
            assert len(scores) <= 3
            assert all(isinstance(score, tuple) and len(score) == 2 for score in scores)
            
            print(f"DEBUG: BM25 검색 결과 {len(scores)}개")
        except Exception as e:
            print(f"ERROR: {str(e)}")
            raise
    
    @pytest.mark.asyncio
    async def test_hybrid_search_engine(self, sample_products):
        try:
            hybrid_engine = HybridSearchEngine()
            
            # 인덱스 구축
            await hybrid_engine.build_index(sample_products)
            
            # 하이브리드 검색 수행
            query = "사무용 의자"
            results = await hybrid_engine.search(query, k=2, alpha=0.5)
            
            assert len(results) <= 2
            assert all("product" in result and "score" in result for result in results)
            
            print(f"DEBUG: 하이브리드 검색 결과 {len(results)}개")
        except Exception as e:
            print(f"ERROR: {str(e)}")
            raise
    
    @pytest.mark.asyncio
    async def test_advanced_rag_module(self, sample_products):
        try:
            rag_module = AdvancedRAGModule()
            
            # 제품 인덱싱
            await rag_module.index_products(sample_products)
            
            # 하이브리드 검색
            search_results = await rag_module.hybrid_search("사무용품", k=2)
            
            assert isinstance(search_results, list)
            assert len(search_results) <= 2
            
            print(f"DEBUG: 고급 RAG 검색 결과 {len(search_results)}개")
        except Exception as e:
            print(f"ERROR: {str(e)}")
            raise
    
    @pytest.mark.asyncio
    async def test_product_matching(self, sample_products):
        try:
            rag_module = AdvancedRAGModule()
            await rag_module.index_products(sample_products)
            
            # 매칭 요구사항
            requirements = {
                "category": "사무용품",
                "budget_max": 150000,
                "specifications": {"재질": "가죽"}
            }
            
            matching_results = await rag_module.match_products_to_requirements(
                sample_products, requirements
            )
            
            assert isinstance(matching_results, list)
            print(f"DEBUG: 매칭 결과 {len(matching_results)}개")
        except Exception as e:
            print(f"ERROR: {str(e)}")
            raise

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
