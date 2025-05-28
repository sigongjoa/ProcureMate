#!/usr/bin/env python3

import pytest
import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

sys.path.append(str(Path(__file__).parent.parent))
from gui.api.handlers import (
    G2BAPIHandler, CoupangAPIHandler, HybridSearchHandler, 
    DocumentGenerationHandler, get_g2b_handler, get_coupang_handler
)

class TestAPIHandlers:
    
    @pytest.fixture
    def g2b_handler(self):
        handler = G2BAPIHandler()
        # 모듈 모킹
        handler.modules = {
            "g2b_api": AsyncMock()
        }
        return handler
    
    @pytest.fixture
    def coupang_handler(self):
        handler = CoupangAPIHandler()
        handler.modules = {
            "coupang_api": AsyncMock()
        }
        return handler
    
    @pytest.fixture
    def hybrid_handler(self):
        handler = HybridSearchHandler()
        handler.modules = {
            "advanced_rag": AsyncMock(),
            "g2b_api": AsyncMock(),
            "coupang_api": AsyncMock()
        }
        return handler
    
    @pytest.fixture
    def doc_handler(self):
        handler = DocumentGenerationHandler()
        handler.modules = {
            "doc_generator": AsyncMock(),
            "llm": AsyncMock()
        }
        return handler
    
    @pytest.mark.asyncio
    async def test_g2b_search_bid_announcements(self, g2b_handler):
        try:
            # 모킹된 응답 설정
            mock_response = {
                "items": [
                    {"id": "bid-001", "title": "사무용품 구매"},
                    {"id": "bid-002", "title": "컴퓨터 구매"}
                ]
            }
            g2b_handler.modules["g2b_api"].get_bid_announcements.return_value = mock_response
            
            # 테스트 실행
            query_params = {"query": "사무용품", "limit": 10}
            result = await g2b_handler.search_bid_announcements(query_params)
            
            assert result["success"] is True
            assert "data" in result
            assert result["total_count"] == 2
            assert "response_time" in result
            
            print("DEBUG: G2B 입찰공고 검색 핸들러 테스트 통과")
        except Exception as e:
            print(f"ERROR: {str(e)}")
            raise
    
    @pytest.mark.asyncio
    async def test_g2b_get_contract_info(self, g2b_handler):
        try:
            mock_response = {"contract_id": "test-123", "status": "active"}
            g2b_handler.modules["g2b_api"].get_contract_info.return_value = mock_response
            
            result = await g2b_handler.get_contract_info("test-123")
            
            assert result["success"] is True
            assert result["data"]["contract_id"] == "test-123"
            
            print("DEBUG: G2B 계약정보 조회 핸들러 테스트 통과")
        except Exception as e:
            print(f"ERROR: {str(e)}")
            raise
    
    @pytest.mark.asyncio
    async def test_coupang_search_products(self, coupang_handler):
        try:
            mock_response = [
                {"id": "prod-001", "name": "사무용 의자", "price": 100000},
                {"id": "prod-002", "name": "사무용 책상", "price": 200000}
            ]
            coupang_handler.modules["coupang_api"].search_products.return_value = mock_response
            
            result = await coupang_handler.search_products("사무용 의자", limit=20)
            
            assert result["success"] is True
            assert result["total_count"] == 2
            assert len(result["data"]) == 2
            
            print("DEBUG: 쿠팡 상품 검색 핸들러 테스트 통과")
        except Exception as e:
            print(f"ERROR: {str(e)}")
            raise
    
    @pytest.mark.asyncio
    async def test_coupang_get_product_details(self, coupang_handler):
        try:
            mock_response = {
                "id": "prod-123", 
                "name": "테스트 상품",
                "price": 50000,
                "specifications": {"색상": "검정"}
            }
            coupang_handler.modules["coupang_api"].get_product_details.return_value = mock_response
            
            result = await coupang_handler.get_product_details("prod-123")
            
            assert result["success"] is True
            assert result["data"]["id"] == "prod-123"
            
            print("DEBUG: 쿠팡 상품 상세정보 핸들러 테스트 통과")
        except Exception as e:
            print(f"ERROR: {str(e)}")
            raise
    
    @pytest.mark.asyncio
    async def test_hybrid_search_all_platforms(self, hybrid_handler):
        try:
            # 각 모듈의 응답 모킹
            hybrid_handler.modules["advanced_rag"].hybrid_search.return_value = [
                {"product": "rag-001", "score": 0.9}
            ]
            hybrid_handler.modules["g2b_api"].search_products.return_value = [
                {"id": "g2b-001", "name": "G2B 상품"}
            ]
            hybrid_handler.modules["coupang_api"].search_products.return_value = [
                {"id": "cp-001", "name": "쿠팡 상품"}
            ]
            
            result = await hybrid_handler.search_all_platforms("사무용품")
            
            assert result["success"] is True
            assert "data" in result
            assert result["data"]["total_found"] == 3
            
            print("DEBUG: 하이브리드 검색 핸들러 테스트 통과")
        except Exception as e:
            print(f"ERROR: {str(e)}")
            raise
    
    @pytest.mark.asyncio
    async def test_procurement_matching_analysis(self, hybrid_handler):
        try:
            mock_matching_result = {
                "matches": [
                    {"product_id": "p1", "score": 0.85, "reasons": ["가격 적합", "사양 일치"]}
                ]
            }
            hybrid_handler.modules["advanced_rag"].match_products_to_requirements.return_value = mock_matching_result
            
            products = [{"id": "p1", "name": "테스트 상품"}]
            requirements = {"budget_max": 100000, "category": "사무용품"}
            
            result = await hybrid_handler.analyze_procurement_match(products, requirements)
            
            assert result["success"] is True
            assert "data" in result
            
            print("DEBUG: 조달 매칭 분석 핸들러 테스트 통과")
        except Exception as e:
            print(f"ERROR: {str(e)}")
            raise
    
    @pytest.mark.asyncio
    async def test_generate_procurement_report(self, doc_handler):
        try:
            mock_report = {
                "report_id": "report-123",
                "content": "조달 보고서 내용",
                "generated_at": "2025-05-26"
            }
            doc_handler.modules["doc_generator"].generate_procurement_report.return_value = mock_report
            
            products = [{"id": "p1", "name": "테스트 상품"}]
            requirements = {"budget": 100000}
            
            result = await doc_handler.generate_procurement_report(products, requirements)
            
            assert result["success"] is True
            assert result["data"]["report_id"] == "report-123"
            
            print("DEBUG: 조달 보고서 생성 핸들러 테스트 통과")
        except Exception as e:
            print(f"ERROR: {str(e)}")
            raise
    
    @pytest.mark.asyncio
    async def test_create_comparison_document(self, doc_handler):
        try:
            mock_comparison = {
                "document_id": "comp-456",
                "comparison_table": "비교 테이블 데이터"
            }
            doc_handler.modules["doc_generator"].create_comparison_document.return_value = mock_comparison
            
            comparison_data = {
                "products": [
                    {"name": "상품A", "price": 100000},
                    {"name": "상품B", "price": 120000}
                ]
            }
            
            result = await doc_handler.create_comparison_document(comparison_data)
            
            assert result["success"] is True
            assert result["data"]["document_id"] == "comp-456"
            
            print("DEBUG: 비교 문서 생성 핸들러 테스트 통과")
        except Exception as e:
            print(f"ERROR: {str(e)}")
            raise
    
    def test_singleton_handlers(self):
        try:
            # 싱글톤 패턴 테스트
            handler1 = get_g2b_handler()
            handler2 = get_g2b_handler()
            
            assert handler1 is handler2
            
            coupang1 = get_coupang_handler()
            coupang2 = get_coupang_handler()
            
            assert coupang1 is coupang2
            
            print("DEBUG: 핸들러 싱글톤 패턴 테스트 통과")
        except Exception as e:
            print(f"ERROR: {str(e)}")
            raise
    
    @pytest.mark.asyncio
    async def test_error_handling(self, g2b_handler):
        try:
            # 에러 발생 시뮬레이션
            g2b_handler.modules["g2b_api"].get_bid_announcements.side_effect = Exception("API 에러")
            
            result = await g2b_handler.search_bid_announcements({"query": "test"})
            
            assert result["success"] is False
            assert "error" in result
            assert "response_time" in result
            
            print("DEBUG: 에러 처리 테스트 통과")
        except Exception as e:
            print(f"ERROR: {str(e)}")
            raise

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
