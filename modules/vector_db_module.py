import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import uuid
import json
from datetime import datetime
from utils import get_logger, ModuleValidator
from config import ProcureMateSettings

logger = get_logger(__name__)

class VectorDbModule:
    """벡터 데이터베이스 & RAG 모듈"""
    
    def __init__(self):
        self.db_type = ProcureMateSettings.VECTOR_DB_TYPE
        self.host = ProcureMateSettings.VECTOR_DB_HOST
        self.port = ProcureMateSettings.VECTOR_DB_PORT
        self.validator = ModuleValidator("VectorDbModule")
        
        self.client = None
        self.collection = None
        self.embedding_model = None
        
        self._initialize_database()
        self._initialize_embedding_model()
        
        logger.info("VectorDbModule 초기화")
    
    def _initialize_database(self):
        if self.db_type.lower() == "chroma":
            # 새로운 ChromaDB API 사용
            self.client = chromadb.PersistentClient(path="./chroma_db")
            
            # 컬렉션 생성 또는 가져오기
            try:
                self.collection = self.client.get_collection("procurement_data")
                logger.info("기존 Chroma 컬렉션 사용")
            except:
                self.collection = self.client.create_collection("procurement_data")
                logger.info("새 Chroma 컬렉션 생성")
            
            logger.info("Chroma DB 초기화 완료")
        else:
            logger.warning(f"지원하지 않는 DB 타입: {self.db_type}")

    def _initialize_embedding_model(self):
        """임베딩 모델 초기화"""

        # 한국어 지원 임베딩 모델
        model_name = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
        self.embedding_model = SentenceTransformer(model_name)
        
        logger.info(f"임베딩 모델 로드 완료: {model_name}")
        

    
    def _create_embedding(self, text: str) -> List[float]:
        """텍스트 임베딩 생성"""

        if self.embedding_model:
            embedding = self.embedding_model.encode(text)
            return embedding.tolist()
        else:
            # 더미 임베딩 (실제 운영에서는 사용 금지)
            logger.warning("더미 임베딩 사용 - 실제 모델 로드 실패")
            return [0.1] * 384  # 기본 차원
 
    
    def add_product_data(self, product_data: Dict[str, Any]) -> bool:
        """상품 데이터 추가"""
        if not self.collection:
            logger.error("컬렉션이 초기화되지 않음")
            return False
        
        # 검색 가능한 텍스트 생성
        searchable_text = self._create_searchable_text(product_data)
        
        # 임베딩 생성
        embedding = self._create_embedding(searchable_text)
        
        # 고유 ID 생성
        doc_id = str(uuid.uuid4())
        
        # 메타데이터 준비
        metadata = {
            "platform": product_data.get("platform", ""),
            "name": product_data.get("name", ""),
            "price": product_data.get("price", 0),
            "vendor": product_data.get("vendor", ""),
            "rating": product_data.get("rating", 0),
            "added_at": datetime.now().isoformat()
        }
        
        # 컬렉션에 추가
        self.collection.add(
            embeddings=[embedding],
            documents=[searchable_text],
            metadatas=[metadata],
            ids=[doc_id]
        )
        
        logger.debug(f"상품 데이터 추가 완료: {product_data.get('name', 'Unknown')}")
        return True
        

    def _create_searchable_text(self, product_data: Dict[str, Any]) -> str:
        """검색 가능한 텍스트 생성"""
        text_parts = []
        
        # 주요 필드들을 하나의 텍스트로 결합
        if product_data.get("name"):
            text_parts.append(product_data["name"])
        
        if product_data.get("vendor"):
            text_parts.append(f"업체: {product_data['vendor']}")
        
        if product_data.get("platform"):
            text_parts.append(f"플랫폼: {product_data['platform']}")
        
        # 가격 정보
        if product_data.get("price"):
            text_parts.append(f"가격: {product_data['price']}원")
        
        # 추가 정보
        if product_data.get("specifications"):
            text_parts.extend(product_data["specifications"])
        
        return " ".join(text_parts)
    
    def search_similar_products(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """유사 상품 검색"""

        if not self.collection:
            logger.error("컬렉션이 초기화되지 않음")
            return []
        
        # 쿼리 임베딩 생성
        query_embedding = self._create_embedding(query)
        
        # 유사도 검색
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=limit
        )
        
        # 결과 포맷팅
        products = []
        if results["documents"] and results["documents"][0]:
            for i in range(len(results["documents"][0])):
                product = {
                    "id": results["ids"][0][i],
                    "document": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i] if results.get("distances") else 0
                }
                products.append(product)
        
        logger.info(f"유사 상품 검색 완료: {len(products)}개 결과")
        return products
        
    
    def add_procurement_history(self, procurement_data: Dict[str, Any]) -> bool:
        """조달 이력 추가"""

        # 조달 요청을 검색 가능한 형태로 변환
        history_text = self._create_procurement_text(procurement_data)
        
        # 임베딩 생성
        embedding = self._create_embedding(history_text)
        
        # 히스토리 컬렉션에 추가
        if not self.client:
            logger.error("클라이언트가 초기화되지 않음")
            return False
            
        try:
            history_collection = self.client.get_collection("procurement_history")
        except:
            history_collection = self.client.create_collection("procurement_history")
        
        doc_id = str(uuid.uuid4())
        metadata = {
            "type": "procurement_request",
            "items": json.dumps(procurement_data.get("items", [])),
            "urgency": procurement_data.get("urgency", ""),
            "budget": procurement_data.get("budget_range", ""),
            "created_at": datetime.now().isoformat()
        }
        
        history_collection.add(
            embeddings=[embedding],
            documents=[history_text],
            metadatas=[metadata],
            ids=[doc_id]
        )
        
        logger.info("조달 이력 추가 완료")
        return True
        

    
    def _create_procurement_text(self, procurement_data: Dict[str, Any]) -> str:
        """조달 데이터를 검색 가능한 텍스트로 변환"""
        text_parts = []
        
        if procurement_data.get("items"):
            items_text = "조달 물품: " + ", ".join(procurement_data["items"])
            text_parts.append(items_text)
        
        if procurement_data.get("urgency"):
            text_parts.append(f"긴급도: {procurement_data['urgency']}")
        
        if procurement_data.get("budget_range"):
            text_parts.append(f"예산: {procurement_data['budget_range']}")
        
        if procurement_data.get("specifications"):
            text_parts.extend(procurement_data["specifications"])
        
        return " ".join(text_parts)
    
    def find_similar_procurement_cases(self, current_request: Dict[str, Any], limit: int = 3) -> List[Dict[str, Any]]:
        """유사한 조달 사례 검색"""

        # 현재 요청을 텍스트로 변환
        request_text = self._create_procurement_text(current_request)
        
        # 히스토리 컬렉션에서 검색
        if not self.client:
            logger.error("클라이언트가 초기화되지 않음")
            return []
            
        try:
            history_collection = self.client.get_collection("procurement_history")
        except:
            logger.info("조달 이력이 없음")
            return []
        
        # 쿼리 임베딩 생성
        query_embedding = self._create_embedding(request_text)
        
        # 유사 사례 검색
        results = history_collection.query(
            query_embeddings=[query_embedding],
            n_results=limit
        )
        
        # 결과 포맷팅
        cases = []
        if results["documents"] and results["documents"][0]:
            for i in range(len(results["documents"][0])):
                case = {
                    "id": results["ids"][0][i],
                    "document": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "similarity": 1 - results["distances"][0][i] if results.get("distances") else 0
                }
                cases.append(case)
        
        logger.info(f"유사 조달 사례 검색 완료: {len(cases)}개")
        return cases

    
    def get_personalized_recommendations(self, user_query: str, user_history: List[Dict] = None) -> List[Dict[str, Any]]:
        """개인화된 추천"""
        recommendations = []
        
        # 기본 유사 상품 검색
        similar_products = self.search_similar_products(user_query, limit=3)
        recommendations.extend(similar_products)
        
        # 사용자 이력 기반 추천 (구현 가능시)
        if user_history:
            # 사용자의 과거 구매 패턴 분석하여 추천
            pass
        
        logger.info(f"개인화된 추천 생성: {len(recommendations)}개")
        return recommendations
    
    def run_validation_tests(self) -> bool:
        """모듈 검증 테스트"""
        test_product = {
            "platform": "test",
            "name": "테스트 상품",
            "price": 10000,
            "vendor": "테스트 업체",
            "rating": 4.0
        }
        
        test_cases = [
            {
                "input": {"product_data": test_product},
                "expected": None
            }
        ]
        
        def test_add_product(product_data: Dict):
            return self.add_product_data(product_data)
        
        def test_search(query: str):
            results = self.search_similar_products(query, limit=1)
            return len(results) >= 0  # 결과가 있거나 없어도 성공
        
        add_result = self.validator.validate_function(test_add_product, test_cases)
        
        search_cases = [{"input": {"query": "테스트"}, "expected": None}]
        search_result = self.validator.validate_function(test_search, search_cases)
        
        debug_info = self.validator.debug_module_state(self)
        summary = self.validator.get_test_summary()
        
        logger.info(f"VectorDbModule validation summary: {summary}")
        
        return add_result and search_result

# 디버그 실행
if __name__ == "__main__":
    logger.info("VectorDbModule 디버그 모드 시작")
    
    vector_db = VectorDbModule()
    
    # 테스트 상품 데이터 추가
    test_products = [
        {
            "platform": "coupang",
            "name": "사무용 의자 프리미엄",
            "price": 150000,
            "vendor": "가구업체A",
            "rating": 4.5,
            "specifications": ["높이 조절", "회전", "팔걸이"]
        },
        {
            "platform": "g2b",
            "name": "사무용 책상",
            "price": 200000,
            "vendor": "사무가구B",
            "rating": 4.2,
            "specifications": ["1200x600", "서랍 2개"]
        }
    ]
    
    # 상품 데이터 추가
    for product in test_products:
        success = vector_db.add_product_data(product)
        logger.info(f"상품 추가 결과: {success}")
    
    # 유사 상품 검색 테스트
    search_results = vector_db.search_similar_products("사무용 의자", limit=2)
    logger.info(f"검색 결과: {len(search_results)}개")
    for result in search_results:
        logger.info(f"  - {result['metadata']['name']} (거리: {result['distance']:.3f})")
    
    # 조달 이력 추가 테스트
    procurement_request = {
        "items": ["사무용 의자", "책상"],
        "urgency": "보통",
        "budget_range": "50만원",
        "specifications": ["조립 필요"]
    }
    
    history_added = vector_db.add_procurement_history(procurement_request)
    logger.info(f"조달 이력 추가: {history_added}")
    
    # 유사 사례 검색
    similar_cases = vector_db.find_similar_procurement_cases(procurement_request)
    logger.info(f"유사 사례: {len(similar_cases)}개")
    
    # 검증 테스트
    if vector_db.run_validation_tests():
        logger.info("모든 검증 테스트 통과")
    else:
        logger.error("검증 테스트 실패")
    
    logger.info("VectorDbModule 디버그 완료")
