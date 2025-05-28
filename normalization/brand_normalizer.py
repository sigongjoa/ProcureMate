#!/usr/bin/env python3
"""
브랜드명 정규화 모듈
"""

from typing import Dict, List, Optional
from .similarity_mapping import SimilarityMappingSystem
from utils import get_logger

logger = get_logger(__name__)

class BrandNormalizer:
    """브랜드명 정규화"""
    
    def __init__(self):
        self.mapping_system = SimilarityMappingSystem()
        self.is_initialized = False
    
    async def initialize(self):
        """초기화"""
        await self.mapping_system.initialize()
        await self._ensure_brand_rules()
        self.is_initialized = True
        logger.info("브랜드명 정규화 모듈 초기화 완료")
    
    async def _ensure_brand_rules(self):
        """브랜드 규칙 확인 및 추가"""
        brand_mappings = {
            "삼성": ["Samsung", "SAMSUNG", "삼성전자", "삼성"],
            "엘지": ["LG", "엘지전자", "LG전자", "엘지"],
            "한국HP": ["HP Korea", "한국휴렛팩커드", "HP", "hp"],
            "애플": ["Apple", "APPLE", "apple", "애플"],
            "마이크로소프트": ["Microsoft", "MS", "microsoft", "MICROSOFT"],
            "소니": ["Sony", "SONY", "sony", "소니"],
            "구글": ["Google", "GOOGLE", "google", "구글"],
            "아마존": ["Amazon", "AMAZON", "amazon", "아마존"],
            "인텔": ["Intel", "INTEL", "intel", "인텔"],
            "AMD": ["amd", "Advanced Micro Devices", "에이엠디"],
            "NVIDIA": ["nvidia", "엔비디아", "Nvidia"],
            "화웨이": ["Huawei", "HUAWEI", "huawei", "화웨이"],
            "샤오미": ["Xiaomi", "XIAOMI", "xiaomi", "샤오미"],
            "레노버": ["Lenovo", "LENOVO", "lenovo", "레노버"],
            "델": ["Dell", "DELL", "dell", "델"],
            "아수스": ["ASUS", "asus", "Asus", "아수스"],
            "에이서": ["Acer", "ACER", "acer", "에이서"]
        }
        
        for standard, variants in brand_mappings.items():
            for variant in variants:
                await self.mapping_system.add_new_variant(standard, variant, "brands")
    
    async def normalize_brand(self, brand_text: str) -> str:
        """브랜드명 정규화"""
        if not self.is_initialized:
            await self.initialize()
        
        return await self.mapping_system.normalize_term(brand_text, "brands")
    
    async def detect_brands_in_text(self, text: str) -> List[Dict]:
        """텍스트에서 브랜드 감지 및 정규화"""
        if not self.is_initialized:
            await self.initialize()
        
        detected_brands = []
        words = text.split()
        
        for word in words:
            normalized = await self.normalize_brand(word)
            if normalized != word:
                detected_brands.append({
                    "original": word,
                    "normalized": normalized,
                    "category": "brand"
                })
        
        return detected_brands
    
    async def suggest_brand_normalization(self, brand_text: str) -> List[Dict]:
        """브랜드명 정규화 제안"""
        if not self.is_initialized:
            await self.initialize()
        
        return await self.mapping_system.suggest_normalization(brand_text, "brands")
