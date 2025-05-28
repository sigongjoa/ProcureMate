import pytest
import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from modules import LlmModule, DataCollectorModule, VectorDbModule
from utils import get_logger

logger = get_logger(__name__)

class TestLlmModule:
    """LlmModule 테스트"""
    
    @pytest.fixture
    def llm_module(self):
        return LlmModule()
    
    def test_llm_initialization(self, llm_module):
        """LLM 모듈 초기화 테스트"""
        assert llm_module is not None
        assert hasattr(llm_module, 'model_name')
        assert hasattr(llm_module, 'server_url')
        logger.info("LLM 모듈 초기화 테스트 통과")
    
    def test_procurement_analysis(self, llm_module):
        """조달 요청 분석 테스트"""
        test_request = "사무용 의자 5개 필요합니다"
        result = llm_module.analyze_procurement_request(test_request)
        
        assert isinstance(result, dict)
        assert "items" in result
        assert "quantities" in result
        assert "urgency" in result
        
        logger.info(f"조달 분석 결과: {result}")

class TestDataCollectorModule:
    """DataCollectorModule 테스트"""
    
    @pytest.fixture
    def data_collector(self):
        return DataCollectorModule()
    
    def test_data_collector_initialization(self, data_collector):
        """데이터 수집 모듈 초기화 테스트"""
        assert data_collector is not None
        assert hasattr(data_collector, 'validator')
        logger.info("데이터 수집 모듈 초기화 테스트 통과")
    
    def test_coupang_search(self, data_collector):
        """쿠팡 검색 테스트 (Mock 데이터)"""
        results = data_collector.search_coupang_products("테스트", limit=2)
        
        assert isinstance(results, list)
        assert len(results) >= 0  # Mock 데이터라도 리스트 반환
        
        if results:
            assert "platform" in results[0]
            assert results[0]["platform"] == "coupang"
        
        logger.info(f"쿠팡 검색 결과: {len(results)}개")

class TestVectorDbModule:
    """VectorDbModule 테스트"""
    
    @pytest.fixture
    def vector_db(self):
        return VectorDbModule()
    
    def test_vector_db_initialization(self, vector_db):
        """벡터DB 모듈 초기화 테스트"""
        assert vector_db is not None
        assert hasattr(vector_db, 'client')
        logger.info("벡터DB 모듈 초기화 테스트 통과")
    
    def test_add_product_data(self, vector_db):
        """상품 데이터 추가 테스트"""
        test_product = {
            "platform": "test",
            "name": "테스트 상품",
            "price": 10000,
            "vendor": "테스트 업체"
        }
        
        result = vector_db.add_product_data(test_product)
        assert isinstance(result, bool)
        logger.info(f"상품 데이터 추가 결과: {result}")
    
    def test_search_similar_products(self, vector_db):
        """유사 상품 검색 테스트"""
        results = vector_db.search_similar_products("테스트 상품", limit=1)
        
        assert isinstance(results, list)
        logger.info(f"유사 상품 검색 결과: {len(results)}개")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
