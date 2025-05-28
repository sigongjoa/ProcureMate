#!/usr/bin/env python3
"""
통합 텍스트 전처리기
"""

import re
from typing import Dict, List, Optional
from .color_normalizer import ColorNormalizer
from .brand_normalizer import BrandNormalizer
from .unit_normalizer import UnitNormalizer
from utils import get_logger

logger = get_logger(__name__)

class UnifiedTextProcessor:
    """통합 텍스트 전처리기"""
    
    def __init__(self):
        self.color_normalizer = ColorNormalizer()
        self.brand_normalizer = BrandNormalizer()
        self.unit_normalizer = UnitNormalizer()
        self.is_initialized = False
    
    async def initialize(self):
        """전체 시스템 초기화"""
        await self.color_normalizer.initialize()
        await self.brand_normalizer.initialize()
        await self.unit_normalizer.initialize()
        self.is_initialized = True
        logger.info("통합 텍스트 전처리기 초기화 완료")
    
    async def process_text(self, text: str) -> Dict[str, str]:
        """텍스트 전체 처리"""
        if not self.is_initialized:
            await self.initialize()
        
        if not text:
            return {"original": "", "normalized": "", "searchable": ""}
        
        original = text.strip()
        
        # 1. 기본 정규화
        normalized = self._basic_normalize(original)
        
        # 2. 브랜드명 정규화
        normalized = await self._normalize_brands_in_text(normalized)
        
        # 3. 색상 정규화
        normalized = await self._normalize_colors_in_text(normalized)
        
        # 4. 단위 정규화
        normalized = await self.unit_normalizer.normalize_quantity_expression(normalized)
        
        # 5. 검색용 텍스트 생성
        searchable = self._create_searchable_text(normalized)
        
        return {
            "original": original,
            "normalized": normalized,
            "searchable": searchable
        }
    
    def _basic_normalize(self, text: str) -> str:
        """기본 정규화"""
        # 특수문자 제거 (하이픈, 점, 괄호는 유지)
        text = re.sub(r'[^\w\s가-힣\-\.\(\)]', ' ', text)
        
        # 연속된 공백 제거
        text = re.sub(r'\s+', ' ', text)
        
        # 불필요한 단어 제거
        unnecessary_words = ['신상품', '특가', '할인', '무료배송', '당일배송', '인기상품']
        for word in unnecessary_words:
            text = text.replace(word, '')
        
        return text.strip()
    
    async def _normalize_brands_in_text(self, text: str) -> str:
        """텍스트 내 브랜드명 정규화"""
        brands = await self.brand_normalizer.detect_brands_in_text(text)
        
        for brand_info in brands:
            text = text.replace(brand_info["original"], brand_info["normalized"])
        
        return text
    
    async def _normalize_colors_in_text(self, text: str) -> str:
        """텍스트 내 색상 정규화"""
        colors = await self.color_normalizer.detect_colors_in_text(text)
        
        for color_info in colors:
            text = text.replace(color_info["original"], color_info["normalized"])
        
        return text
    
    def _create_searchable_text(self, text: str) -> str:
        """검색용 텍스트 생성"""
        # 한글, 영문, 숫자만 유지
        searchable = re.sub(r'[^\w가-힣]', ' ', text)
        
        # 연속 공백 제거
        searchable = re.sub(r'\s+', ' ', searchable)
        
        return searchable.strip().lower()
    
    async def get_normalization_analysis(self, text: str) -> Dict:
        """정규화 분석 결과"""
        if not self.is_initialized:
            await self.initialize()
        
        brands = await self.brand_normalizer.detect_brands_in_text(text)
        colors = await self.color_normalizer.detect_colors_in_text(text)
        units = await self.unit_normalizer.detect_units_in_text(text)
        
        return {
            "original_text": text,
            "detected_brands": brands,
            "detected_colors": colors,
            "detected_units": units,
            "total_normalizations": len(brands) + len(colors) + len(units)
        }
    
    async def suggest_improvements(self, text: str) -> List[Dict]:
        """개선 제안"""
        if not self.is_initialized:
            await self.initialize()
        
        suggestions = []
        words = text.split()
        
        for word in words:
            # 브랜드명 제안
            brand_suggestions = await self.brand_normalizer.suggest_brand_normalization(word)
            suggestions.extend(brand_suggestions)
            
            # 색상 제안
            color_suggestions = await self.color_normalizer.suggest_color_normalization(word)
            suggestions.extend(color_suggestions)
            
            # 단위 제안
            unit_suggestions = await self.unit_normalizer.suggest_unit_normalization(word)
            suggestions.extend(unit_suggestions)
        
        # 중복 제거 및 정렬
        unique_suggestions = []
        seen = set()
        
        for suggestion in suggestions:
            key = (suggestion["original"], suggestion["suggested"])
            if key not in seen:
                seen.add(key)
                unique_suggestions.append(suggestion)
        
        return sorted(unique_suggestions, key=lambda x: x["similarity"], reverse=True)
