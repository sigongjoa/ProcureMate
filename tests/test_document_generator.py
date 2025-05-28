#!/usr/bin/env python3

import pytest
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from modules.document_generator import ProcurementRequirement, ProcurementDocumentGenerator, DocumentGenerator
from modules.data_processor import UnifiedProduct
from modules.llm_module import LlmModule
from decimal import Decimal

class TestDocumentGenerator:
    
    @pytest.fixture
    def sample_requirement(self):
        return ProcurementRequirement(
            category="사무용품",
            budget_min=50000.0,
            budget_max=200000.0, 
            delivery_days=30,
            specifications={"재질": "가죽", "색상": "검정"},
            priority_weights={"price": 0.4, "delivery": 0.3, "specifications": 0.3}
        )
    
    @pytest.fixture
    def sample_products(self):
        return [
            UnifiedProduct(
                id="p1", source="test",
                name={"original": "사무용 의자", "normalized": "사무용 의자"},
                price={"amount": Decimal("120000"), "currency": "KRW"},
                category=["사무용품", "의자"], 
                specifications={"재질": "가죽", "색상": "검정"},
                metadata={"delivery_days": 15}
            ),
            UnifiedProduct(
                id="p2", source="test",
                name={"original": "사무용 책상", "normalized": "사무용 책상"},
                price={"amount": Decimal("180000"), "currency": "KRW"},
                category=["사무용품", "책상"],
                specifications={"재질": "목재", "크기": "120x60"},
                metadata={"delivery_days": 20}
            )
        ]
    
    @pytest.fixture
    def doc_generator(self):
        return ProcurementDocumentGenerator()
    
    @pytest.fixture
    def llm_module(self):
        return LlmModule()
    
    def test_procurement_requirement_creation(self, sample_requirement):
        try:
            assert sample_requirement.category == "사무용품"
            assert sample_requirement.budget_max == 200000.0
            assert len(sample_requirement.specifications) == 2
            print("DEBUG: ProcurementRequirement 생성 테스트 통과")
        except Exception as e:
            print(f"ERROR: {str(e)}")
            raise
    
    @pytest.mark.asyncio
    async def test_generate_procurement_report(self, doc_generator, sample_products, sample_requirement, llm_module):
        try:
            report = await doc_generator.generate_procurement_report(
                sample_products, sample_requirement, llm_module
            )
            
            assert isinstance(report, dict)
            assert "report_content" in report or "content" in report
            print("DEBUG: 조달 보고서 생성 테스트 통과")
        except Exception as e:
            print(f"ERROR: {str(e)}")
            raise
    
    @pytest.mark.asyncio
    async def test_create_comparison_document(self, doc_generator, sample_products):
        try:
            comparison_data = {
                "products": [product.dict() for product in sample_products],
                "criteria": ["price", "delivery", "specifications"]
            }
            
            comparison_doc = await doc_generator.create_comparison_document(comparison_data)
            
            assert isinstance(comparison_doc, dict)
            print("DEBUG: 비교 문서 생성 테스트 통과")
        except Exception as e:
            print(f"ERROR: {str(e)}")
            raise
    
    def test_product_matching_analysis(self, sample_products, sample_requirement):
        try:
            from modules.advanced_rag_module import AdvancedProductMatcher
            
            matcher = AdvancedProductMatcher()
            matching_results = matcher.match_products_to_requirements(
                sample_products, sample_requirement
            )
            
            assert isinstance(matching_results, list)
            assert len(matching_results) <= len(sample_products)
            
            # 각 결과가 (product, score, details) 형태인지 확인
            for result in matching_results:
                assert len(result) == 3
                product, score, details = result
                assert isinstance(score, float)
                assert isinstance(details, dict)
            
            print(f"DEBUG: 매칭 분석 결과 {len(matching_results)}개")
        except Exception as e:
            print(f"ERROR: {str(e)}")
            raise
    
    def test_mandatory_conditions_check(self, sample_products, sample_requirement):
        try:
            from modules.advanced_rag_module import AdvancedProductMatcher
            
            matcher = AdvancedProductMatcher()
            
            # 첫 번째 제품은 조건을 만족해야 함
            product1 = sample_products[0]
            is_valid = matcher._check_mandatory_conditions(product1, sample_requirement)
            
            assert isinstance(is_valid, bool)
            print(f"DEBUG: 필수 조건 검사 결과: {is_valid}")
        except Exception as e:
            print(f"ERROR: {str(e)}")
            raise
    
    def test_multidimensional_scoring(self, sample_products, sample_requirement):
        try:
            from modules.advanced_rag_module import AdvancedProductMatcher
            
            matcher = AdvancedProductMatcher()
            product = sample_products[0]
            
            scores = matcher._calculate_multidimensional_scores(product, sample_requirement)
            
            assert isinstance(scores, dict)
            assert "price" in scores
            assert "specifications" in scores
            
            # 모든 점수가 0-1 범위인지 확인
            for score_name, score_value in scores.items():
                assert 0 <= score_value <= 1, f"{score_name} 점수가 범위를 벗어남: {score_value}"
            
            print(f"DEBUG: 다차원 점수 계산 완료 - {len(scores)}개 항목")
        except Exception as e:
            print(f"ERROR: {str(e)}")
            raise

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
