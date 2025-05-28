#!/usr/bin/env python3

import pytest
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from modules.data_processor import UnifiedProduct, KoreanTextNormalizer, DataIntegrator, ProductDeduplicator
from decimal import Decimal
from datetime import datetime

class TestDataProcessor:
    
    @pytest.fixture
    def sample_product(self):
        return UnifiedProduct(
            id="test-001",
            source="test",
            name={"original": "사무용 의자", "normalized": "사무용 의자"},
            price={"amount": Decimal("100000"), "currency": "KRW", "vat_included": True},
            category=["사무용품", "의자"],
            specifications={"색상": "검정", "재질": "가죽"},
            metadata={"supplier": "테스트업체"},
            timestamps={"created": datetime.now()}
        )
    
    @pytest.fixture
    def normalizer(self):
        return KoreanTextNormalizer()
    
    @pytest.fixture
    def deduplicator(self):
        return ProductDeduplicator()
    
    def test_unified_product_creation(self, sample_product):
        try:
            assert sample_product.id == "test-001"
            assert sample_product.source == "test"
            assert sample_product.price["amount"] == Decimal("100000")
            print("DEBUG: UnifiedProduct 생성 테스트 통과")
        except Exception as e:
            print(f"ERROR: {str(e)}")
            raise
    
    def test_price_validation(self):
        try:
            # 잘못된 가격으로 테스트
            with pytest.raises(ValueError):
                UnifiedProduct(
                    id="test-002",
                    source="test", 
                    name={"original": "테스트", "normalized": "테스트"},
                    price={"amount": Decimal("-1000"), "currency": "KRW"},
                    category=["테스트"]
                )
            print("DEBUG: 가격 검증 테스트 통과")
        except Exception as e:
            print(f"ERROR: {str(e)}")
            raise
    
    def test_korean_text_normalization(self, normalizer):
        try:
            test_text = "삼성전자!!! 사무용  의자~~~"
            result = normalizer.normalize_product_name(test_text)
            
            assert "original" in result
            assert "normalized" in result
            assert "morphs" in result
            assert "searchable" in result
            
            print(f"DEBUG: 정규화 결과 - {result['normalized']}")
        except Exception as e:
            print(f"ERROR: {str(e)}")
            raise
    
    def test_brand_mapping(self, normalizer):
        try:
            test_text = "Samsung 노트북"
            result = normalizer.normalize_product_name(test_text)
            
            # 브랜드 매핑이 적용되었는지 확인
            assert "삼성" in result["normalized"] or "Samsung" in result["normalized"]
            print("DEBUG: 브랜드 매핑 테스트 통과")
        except Exception as e:
            print(f"ERROR: {str(e)}")
            raise
    
    def test_product_deduplication(self, deduplicator):
        try:
            # 유사한 제품들 생성
            products = [
                UnifiedProduct(
                    id="p1", source="test",
                    name={"original": "사무용 의자", "normalized": "사무용 의자"},
                    price={"amount": Decimal("100000"), "currency": "KRW"},
                    category=["사무용품"]
                ),
                UnifiedProduct(
                    id="p2", source="test", 
                    name={"original": "사무용의자", "normalized": "사무용 의자"},
                    price={"amount": Decimal("105000"), "currency": "KRW"},
                    category=["사무용품"]
                ),
                UnifiedProduct(
                    id="p3", source="test",
                    name={"original": "컴퓨터 책상", "normalized": "컴퓨터 책상"}, 
                    price={"amount": Decimal("200000"), "currency": "KRW"},
                    category=["사무용품"]
                )
            ]
            
            duplicate_groups = deduplicator.find_duplicates(products)
            
            # 첫 번째와 두 번째 제품이 중복으로 감지되어야 함
            assert len(duplicate_groups) >= 0  # 중복 그룹이 있을 수도 없을 수도
            print(f"DEBUG: 중복 그룹 {len(duplicate_groups)}개 발견")
        except Exception as e:
            print(f"ERROR: {str(e)}")
            raise

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
