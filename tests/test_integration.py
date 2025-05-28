#!/usr/bin/env python3

import pytest
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

class TestIntegration:
    """전체 시스템 통합 테스트"""
    
    @pytest.mark.asyncio
    async def test_full_procurement_workflow(self):
        """완전한 조달 워크플로우 통합 테스트"""
        try:
            # 1. 모듈 임포트
            from modules.g2b_api_client import G2BAPIClient
            from modules.coupang_api_client import CoupangAPIClient, CoupangAuth
            from modules.data_processor import UnifiedProduct, KoreanTextNormalizer
            from modules.advanced_rag_module import AdvancedRAGModule
            from modules.document_generator import ProcurementDocumentGenerator
            from decimal import Decimal
            
            print("DEBUG: 모든 모듈 임포트 성공")
            
            # 2. 데이터 정규화 테스트
            normalizer = KoreanTextNormalizer()
            test_text = "삼성전자 사무용 의자"
            normalized = normalizer.normalize_product_name(test_text)
            
            assert "normalized" in normalized
            print(f"DEBUG: 텍스트 정규화 완료 - {normalized['normalized']}")
            
            # 3. 샘플 제품 생성
            sample_products = [
                UnifiedProduct(
                    id="integration-001",
                    source="test",
                    name={"original": "사무용 의자", "normalized": "사무용 의자"},
                    price={"amount": Decimal("120000"), "currency": "KRW"},
                    category=["사무용품", "의자"],
                    specifications={"재질": "가죽", "색상": "검정"}
                )
            ]
            
            # 4. RAG 시스템 테스트
            rag_module = AdvancedRAGModule()
            await rag_module.index_products(sample_products)
            
            search_results = await rag_module.hybrid_search("사무용 의자", k=1)
            assert len(search_results) > 0
            print("DEBUG: RAG 검색 완료")
            
            # 5. 문서 생성 테스트
            doc_generator = ProcurementDocumentGenerator()
            
            # 간단한 문서 생성 (LLM 없이)
            comparison_data = {
                "products": [product.dict() for product in sample_products],
                "criteria": ["price", "specifications"]
            }
            
            comparison_doc = await doc_generator.create_comparison_document(comparison_data)
            assert isinstance(comparison_doc, dict)
            print("DEBUG: 문서 생성 완료")
            
            print("SUCCESS: 전체 워크플로우 통합 테스트 통과")
            
        except Exception as e:
            print(f"ERROR: 통합 테스트 실패 - {str(e)}")
            raise
    
    def test_module_imports(self):
        """모든 새 모듈의 임포트 가능성 테스트"""
        try:
            from modules.g2b_api_client import G2BAPIClient
            from modules.coupang_api_client import CoupangAuth, RateLimitedCoupangClient, CoupangAPIClient
            from modules.data_processor import UnifiedProduct, KoreanTextNormalizer, DataIntegrator, ProductDeduplicator
            from modules.advanced_rag_module import KoreanEmbeddingEngine, BM25Scorer, HybridSearchEngine, AdvancedRAGModule
            from modules.document_generator import ProcurementRequirement, ProcurementDocumentGenerator, DocumentGenerator
            from gui.api.handlers import G2BAPIHandler, CoupangAPIHandler, HybridSearchHandler, DocumentGenerationHandler
            
            print("DEBUG: 모든 새 모듈 임포트 성공")
            
        except Exception as e:
            print(f"ERROR: 모듈 임포트 실패 - {str(e)}")
            raise
    
    def test_data_flow(self):
        """데이터 흐름 테스트"""
        try:
            from modules.data_processor import UnifiedProduct, KoreanTextNormalizer
            from decimal import Decimal
            
            # 1. 원본 데이터 생성
            raw_data = {
                "name": "삼성전자!!! 사무용  의자~~~",
                "price": 120000,
                "category": "사무용품"
            }
            
            # 2. 정규화
            normalizer = KoreanTextNormalizer()
            normalized_name = normalizer.normalize_product_name(raw_data["name"])
            
            # 3. 통합 객체 생성
            unified_product = UnifiedProduct(
                id="flow-test-001",
                source="test",
                name=normalized_name,
                price={"amount": Decimal(str(raw_data["price"])), "currency": "KRW"},
                category=[raw_data["category"]]
            )
            
            # 4. 검증
            assert unified_product.id == "flow-test-001"
            assert unified_product.price["amount"] == Decimal("120000")
            assert "normalized" in unified_product.name
            
            print("DEBUG: 데이터 흐름 테스트 통과")
            
        except Exception as e:
            print(f"ERROR: 데이터 흐름 테스트 실패 - {str(e)}")
            raise
    
    def test_configuration_loading(self):
        """설정 로딩 테스트"""
        try:
            import os
            from pathlib import Path
            
            # 환경 변수 확인
            config_items = [
                "G2B_SERVICE_KEY",
                "COUPANG_ACCESS_KEY", 
                "COUPANG_SECRET_KEY",
                "COUPANG_VENDOR_ID"
            ]
            
            missing_configs = []
            for item in config_items:
                if not os.getenv(item):
                    missing_configs.append(item)
            
            if missing_configs:
                print(f"WARNING: 설정되지 않은 환경 변수: {missing_configs}")
            else:
                print("DEBUG: 모든 환경 변수 설정 확인")
            
            # .env.example 파일 존재 확인
            env_example = Path(__file__).parent.parent / ".env.example"
            assert env_example.exists(), ".env.example 파일이 없습니다"
            
            print("DEBUG: 설정 로딩 테스트 통과")
            
        except Exception as e:
            print(f"ERROR: 설정 로딩 테스트 실패 - {str(e)}")
            raise

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
