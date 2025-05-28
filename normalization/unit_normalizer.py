#!/usr/bin/env python3
"""
단위 정규화 모듈
"""

from typing import Dict, List, Optional
import re
from .similarity_mapping import SimilarityMappingSystem
from utils import get_logger

logger = get_logger(__name__)

class UnitNormalizer:
    """단위 정규화"""
    
    def __init__(self):
        self.mapping_system = SimilarityMappingSystem()
        self.is_initialized = False
    
    async def initialize(self):
        """초기화"""
        await self.mapping_system.initialize()
        await self._ensure_unit_rules()
        self.is_initialized = True
        logger.info("단위 정규화 모듈 초기화 완료")
    
    async def _ensure_unit_rules(self):
        """단위 규칙 확인 및 추가"""
        unit_mappings = {
            "개": ["개", "EA", "ea", "대", "매", "장", "piece", "pieces"],
            "세트": ["세트", "SET", "set", "조", "셋"],
            "박스": ["박스", "BOX", "box", "상자", "Box"],
            "킬로그램": ["kg", "킬로", "키로", "킬로그램", "KG", "Kg"],
            "그램": ["g", "그램", "gram", "grams", "G"],
            "미터": ["m", "미터", "메터", "meter", "meters", "M"],
            "센티미터": ["cm", "센티", "센티미터", "CM", "Cm"],
            "밀리미터": ["mm", "밀리", "밀리미터", "MM", "Mm"],
            "리터": ["L", "l", "리터", "liter", "liters"],
            "밀리리터": ["ml", "mL", "밀리리터", "ML"],
            "시간": ["시간", "hour", "hours", "hr", "hrs", "h"],
            "분": ["분", "minute", "minutes", "min", "mins"],
            "초": ["초", "second", "seconds", "sec", "secs", "s"],
            "년": ["년", "year", "years", "yr", "yrs"],
            "월": ["월", "month", "months"],
            "일": ["일", "day", "days"],
            "와트": ["W", "w", "와트", "watt", "watts"],
            "볼트": ["V", "v", "볼트", "volt", "volts"],
            "암페어": ["A", "a", "암페어", "amp", "amps"],
            "인치": ["inch", "inches", "인치", "\"", "''"],
            "피트": ["ft", "feet", "foot", "피트", "'"]
        }
        
        for standard, variants in unit_mappings.items():
            for variant in variants:
                await self.mapping_system.add_new_variant(standard, variant, "units")
    
    async def normalize_unit(self, unit_text: str) -> str:
        """단위 정규화"""
        if not self.is_initialized:
            await self.initialize()
        
        return await self.mapping_system.normalize_term(unit_text, "units")
    
    async def detect_units_in_text(self, text: str) -> List[Dict]:
        """텍스트에서 단위 감지 및 정규화"""
        if not self.is_initialized:
            await self.initialize()
        
        detected_units = []
        
        # 숫자+단위 패턴 검색
        patterns = [
            r'(\d+(?:\.\d+)?)\s*([a-zA-Z가-힣]+)',
            r'(\d+(?:\.\d+)?)\s*([a-zA-Z가-힣"\']+)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                number, unit = match.groups()
                normalized_unit = await self.normalize_unit(unit)
                
                if normalized_unit != unit:
                    detected_units.append({
                        "original": f"{number}{unit}",
                        "normalized": f"{number}{normalized_unit}",
                        "number": number,
                        "unit_original": unit,
                        "unit_normalized": normalized_unit,
                        "category": "unit"
                    })
        
        return detected_units
    
    async def normalize_quantity_expression(self, text: str) -> str:
        """수량 표현 정규화"""
        if not self.is_initialized:
            await self.initialize()
        
        normalized_text = text
        units = await self.detect_units_in_text(text)
        
        for unit_info in units:
            normalized_text = normalized_text.replace(
                unit_info["original"], 
                unit_info["normalized"]
            )
        
        return normalized_text
    
    async def suggest_unit_normalization(self, unit_text: str) -> List[Dict]:
        """단위 정규화 제안"""
        if not self.is_initialized:
            await self.initialize()
        
        return await self.mapping_system.suggest_normalization(unit_text, "units")
