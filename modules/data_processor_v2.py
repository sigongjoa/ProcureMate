#!/usr/bin/env python3
"""
조달 데이터 전처리 및 정규화 시스템 (임베딩 기반 업데이트)
G2B와 쿠팡 데이터를 통합 스키마로 변환
"""

import re
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
import json
from difflib import SequenceMatcher
from normalization import UnifiedTextProcessor
from utils import get_logger

logger = get_logger(__name__)

@dataclass
class UnifiedProduct:
    """통합 상품 데이터 모델"""
    id: str
    source: str  # 'g2b' 또는 'coupang'
    name: Dict[str, str]  # {'original': str, 'normalized': str, 'searchable': str}
    price: Dict[str, Any]  # {'amount': Decimal, 'currency': str, 'vat_included': bool}
    specifications: Dict[str, Any] = field(default_factory=dict)
    category: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamps: Dict[str, datetime] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """딕셔너리로 변환"""
        return {
            'id': self.id,
            'source': self.source,
            'name': self.name,
            'price': {
                'amount': float(self.price['amount']),
                'currency': self.price['currency'],
                'vat_included': self.price.get('vat_included', True)
            },
            'specifications': self.specifications,
            'category': self.category,
            'metadata': self.metadata,
            'timestamps': {k: v.isoformat() for k, v in self.timestamps.items()}
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'UnifiedProduct':
        """딕셔너리에서 생성"""
        return cls(
            id=data['id'],
            source=data['source'],
            name=data['name'],
            price={
                'amount': Decimal(str(data['price']['amount'])),
                'currency': data['price']['currency'],
                'vat_included': data['price'].get('vat_included', True)
            },
            specifications=data.get('specifications', {}),
            category=data.get('category', []),
            metadata=data.get('metadata', {}),
            timestamps={k: datetime.fromisoformat(v) for k, v in data.get('timestamps', {}).items()}
        )

class EmbeddingBasedNormalizer:
    """임베딩 기반 텍스트 정규화 (기존 KoreanTextNormalizer 대체)"""
    
    def __init__(self):
        self.processor = UnifiedTextProcessor()
        self.is_initialized = False
    
    async def initialize(self):
        """정규화 시스템 초기화"""
        await self.processor.initialize()
        self.is_initialized = True
        logger.info("임베딩 기반 정규화 시스템 초기화 완료")
    
    async def normalize_text(self, text: str) -> Dict[str, str]:
        """텍스트 정규화 (기존 메서드와 호환)"""
        if not self.is_initialized:
            await self.initialize()
        
        return await self.processor.process_text(text)

class DataIntegrator:
    """G2B와 쿠팡 데이터 통합"""
    
    def __init__(self):
        self.normalizer = EmbeddingBasedNormalizer()
        self.category_mappings = self._initialize_category_mappings()
    
    def _initialize_category_mappings(self) -> Dict[str, List[str]]:
        """카테고리 매핑 초기화"""
        return {
            "사무용품": ["사무/문구용품", "사무용품", "오피스", "문구"],
            "가구": ["가구/인테리어", "책상/의자", "가구", "인테리어"],
            "전자제품": ["가전디지털", "컴퓨터", "전자제품", "IT"],
            "건설자재": ["건설/시설", "건축자재", "건설", "시설"],
            "차량": ["차량/운송", "자동차", "운송장비", "차량"]
        }
    
    async def integrate_g2b_data(self, g2b_data: Dict) -> List[UnifiedProduct]:
        """G2B 데이터를 통합 형식으로 변환"""
        logger.info("G2B 데이터 통합 처리 시작")
        
        unified_products = []
        items = g2b_data.get('items', [])
        
        for item in items:
            unified_product = await self._convert_g2b_item(item)
            if unified_product:
                unified_products.append(unified_product)

        logger.info(f"G2B 데이터 통합 완료: {len(unified_products)}개")
        return unified_products
    
    async def integrate_coupang_data(self, coupang_data: Dict) -> List[UnifiedProduct]:
        """쿠팡 데이터를 통합 형식으로 변환"""
        logger.info("쿠팡 데이터 통합 처리 시작")
        
        unified_products = []
        items = coupang_data.get('items', [])
        
        for item in items:
            unified_product = await self._convert_coupang_item(item)
            if unified_product:
                unified_products.append(unified_product)

        logger.info(f"쿠팡 데이터 통합 완료: {len(unified_products)}개")
        return unified_products
    
    async def _convert_g2b_item(self, item: Dict) -> Optional[UnifiedProduct]:
        """G2B 아이템을 UnifiedProduct로 변환"""

        # 가격 처리 (G2B는 예산 정보)
        budget = item.get('budget', 0)
        if isinstance(budget, str):
            budget = self._extract_number_from_string(budget)
        
        # 이름 정규화 (임베딩 기반)
        name_info = await self.normalizer.normalize_text(item.get('title', ''))
        
        # 카테고리 매핑
        category = self._map_g2b_category(item)
        
        unified_product = UnifiedProduct(
            id=item.get('id', f"g2b_{datetime.now().timestamp()}"),
            source='g2b',
            name=name_info,
            price={
                'amount': Decimal(str(budget)),
                'currency': 'KRW',
                'vat_included': True
            },
            specifications={
                'bid_method': item.get('bid_method', ''),
                'contract_type': item.get('contract_type', ''),
                'industry_code': item.get('industry_code', ''),
                'region': item.get('region_code', '')
            },
            category=category,
            metadata={
                'organization': item.get('organization', ''),
                'announcement_number': item.get('announcement_number', ''),
                'announcement_date': item.get('announcement_date', ''),
                'deadline': item.get('deadline', ''),
                'procurement_type': 'public_bid'
            },
            timestamps={
                'created': datetime.now(),
                'announcement': self._parse_date(item.get('announcement_date', '')),
                'deadline': self._parse_date(item.get('deadline', ''))
            }
        )
        
        return unified_product

    async def _convert_coupang_item(self, item: Dict) -> Optional[UnifiedProduct]:
        """쿠팡 아이템을 UnifiedProduct로 변환"""
        # 가격 처리
        price = item.get('price', 0)
        if isinstance(price, str):
            price = self._extract_number_from_string(price)
        
        # 이름 정규화 (임베딩 기반)
        name_info = await self.normalizer.normalize_text(item.get('name', ''))
        
        # 카테고리 매핑
        category = self._map_coupang_category(item)
        
        # 사양 정보 추출
        specifications = {
            'vendor': item.get('vendor_name', ''),
            'rating': item.get('rating', 0),
            'review_count': item.get('review_count', 0),
            'delivery_fee': item.get('delivery_fee', 0),
            'is_free_shipping': item.get('is_available', False)
        }
        
        # 할인 정보가 있는 경우 추가
        if item.get('original_price', 0) > price:
            specifications['original_price'] = item.get('original_price', 0)
            specifications['discount_rate'] = item.get('discount_rate', 0)
        
        unified_product = UnifiedProduct(
            id=item.get('id', f"coupang_{datetime.now().timestamp()}"),
            source='coupang',
            name=name_info,
            price={
                'amount': Decimal(str(price)),
                'currency': 'KRW',
                'vat_included': True
            },
            specifications=specifications,
            category=category,
            metadata={
                'product_id': item.get('product_id', ''),
                'url': item.get('url', ''),
                'image_url': item.get('image_url', ''),
                'search_query': item.get('search_query', ''),
                'procurement_type': 'commercial'
            },
            timestamps={
                'created': datetime.now(),
                'retrieved': datetime.now()
            }
        )
        
        return unified_product

    def _map_g2b_category(self, item: Dict) -> List[str]:
        """G2B 카테고리 매핑"""
        industry_code = item.get('industry_code', '')
        title = item.get('title', '').lower()
        
        # 제목에서 카테고리 추론
        for main_category, keywords in self.category_mappings.items():
            for keyword in keywords:
                if keyword in title:
                    return [main_category, 'G2B', industry_code]
        
        # 기본 카테고리
        return ['기타', 'G2B', industry_code]
    
    def _map_coupang_category(self, item: Dict) -> List[str]:
        """쿠팡 카테고리 매핑"""
        category_name = item.get('category_name', '')
        
        # 쿠팡 카테고리를 표준 카테고리로 매핑
        for main_category, keywords in self.category_mappings.items():
            for keyword in keywords:
                if keyword in category_name:
                    return [main_category, '쿠팡', category_name]
        
        # 매핑되지 않은 경우 원본 사용
        return [category_name, '쿠팡'] if category_name else ['기타', '쿠팡']
    
    def _extract_number_from_string(self, text: str) -> float:
        """문자열에서 숫자 추출"""
        if not text:
            return 0.0
        
        # 쉼표 제거 후 숫자 추출
        numbers = re.findall(r'[\d,]+', str(text))
        if numbers:
            return float(numbers[0].replace(',', ''))
        return 0.0
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """날짜 문자열 파싱"""
        if not date_str:
            return None
        

        # 다양한 날짜 형식 지원
        formats = ['%Y%m%d', '%Y-%m-%d', '%Y.%m.%d', '%Y/%m/%d']
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        
        return None

class ProductDeduplicator:
    """상품 중복 제거"""
    
    def __init__(self, similarity_threshold: float = 0.85):
        self.threshold = similarity_threshold
    
    async def find_duplicates(self, products: List[UnifiedProduct]) -> List[List[int]]:
        """중복 상품 그룹 찾기"""
        logger.info(f"중복 검사 시작: {len(products)}개 상품")
        
        duplicate_groups = []
        processed = set()
        
        for i in range(len(products)):
            if i in processed:
                continue
            
            group = [i]
            for j in range(i + 1, len(products)):
                if j in processed:
                    continue
                
                if await self._are_similar(products[i], products[j]):
                    group.append(j)
                    processed.add(j)
            
            if len(group) > 1:
                duplicate_groups.append(group)
                processed.update(group)
        
        logger.info(f"중복 그룹 {len(duplicate_groups)}개 발견")
        return duplicate_groups
    
    async def _are_similar(self, product1: UnifiedProduct, product2: UnifiedProduct) -> bool:
        """두 상품의 유사도 판단"""
        # 1. 이름 유사도
        name_similarity = self._calculate_text_similarity(
            product1.name['normalized'],
            product2.name['normalized']
        )
        
        if name_similarity < 0.7:
            return False
        
        # 2. 가격 유사도 (20% 차이 허용)
        price1 = float(product1.price['amount'])
        price2 = float(product2.price['amount'])
        
        if price1 > 0 and price2 > 0:
            price_ratio = min(price1, price2) / max(price1, price2)
            if price_ratio < 0.8:
                return False
        
        # 3. 카테고리 일치
        if product1.category and product2.category:
            category_match = any(c1 in product2.category for c1 in product1.category)
            if not category_match:
                return False
        
        return name_similarity >= self.threshold
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """텍스트 유사도 계산"""
        if not text1 or not text2:
            return 0.0
        
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

# 사용 예시
async def test_data_integration():
    """데이터 통합 테스트"""
    integrator = DataIntegrator()
    deduplicator = ProductDeduplicator()
    
    # Mock G2B 데이터
    g2b_data = {
        'items': [
            {
                'id': 'g2b_1',
                'title': '사무용 책상 구매',
                'budget': 5000000,
                'organization': '테스트 기관',
                'announcement_date': '20250526'
            }
        ]
    }
    
    # Mock 쿠팡 데이터
    coupang_data = {
        'items': [
            {
                'id': 'coupang_1',
                'name': '사무용 책상 1800x800',
                'price': 450000,
                'category_name': '사무/문구용품',
                'vendor_name': '테스트 판매자'
            }
        ]
    }
    
    # 데이터 통합
    g2b_products = await integrator.integrate_g2b_data(g2b_data)
    coupang_products = await integrator.integrate_coupang_data(coupang_data)
    
    all_products = g2b_products + coupang_products
    
    # 중복 검사
    duplicate_groups = await deduplicator.find_duplicates(all_products)
    
    print(f"총 {len(all_products)}개 상품 통합")
    print(f"중복 그룹: {len(duplicate_groups)}개")
    
    # 결과 출력
    for product in all_products:
        print(f"- {product.source}: {product.name['normalized']} ({product.price['amount']}원)")

if __name__ == "__main__":
    asyncio.run(test_data_integration())
