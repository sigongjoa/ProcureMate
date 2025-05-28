#!/usr/bin/env python3
"""
색상 정규화 모듈
"""

from typing import Dict, List, Optional
from .similarity_mapping import SimilarityMappingSystem
from utils import get_logger

logger = get_logger(__name__)

class ColorNormalizer:
    """색상 정규화"""
    
    def __init__(self):
        self.mapping_system = SimilarityMappingSystem()
        self.is_initialized = False
    
    async def initialize(self):
        """초기화"""
        await self.mapping_system.initialize()
        await self._ensure_color_rules()
        self.is_initialized = True
        logger.info("색상 정규화 모듈 초기화 완료")
    
    async def _ensure_color_rules(self):
        """색상 규칙 확인 및 추가"""
        color_mappings = {
            "흰색": ["화이트", "white", "WHITE", "백색", "하얀색", "화이트색"],
            "검은색": ["블랙", "black", "BLACK", "흑색", "까만색", "블랙색"],
            "파란색": ["블루", "blue", "BLUE", "청색", "파랑", "블루색"],
            "빨간색": ["레드", "red", "RED", "적색", "빨강", "레드색"],
            "노란색": ["옐로우", "yellow", "YELLOW", "황색", "노랑", "옐로우색"],
            "초록색": ["그린", "green", "GREEN", "녹색", "초록", "그린색"],
            "회색": ["그레이", "gray", "GRAY", "grey", "GREY", "회색", "그레이색"],
            "갈색": ["브라운", "brown", "BROWN", "갈색", "브라운색"],
            "보라색": ["퍼플", "purple", "PURPLE", "자주색", "보라", "퍼플색"],
            "분홍색": ["핑크", "pink", "PINK", "분홍", "핑크색"]
        }
        
        for standard, variants in color_mappings.items():
            for variant in variants:
                await self.mapping_system.add_new_variant(standard, variant, "colors")
    
    async def normalize_color(self, color_text: str) -> str:
        """색상 정규화"""
        if not self.is_initialized:
            await self.initialize()
        
        return await self.mapping_system.normalize_term(color_text, "colors")
    
    async def detect_colors_in_text(self, text: str) -> List[Dict]:
        """텍스트에서 색상 감지 및 정규화"""
        if not self.is_initialized:
            await self.initialize()
        
        detected_colors = []
        words = text.split()
        
        for word in words:
            normalized = await self.normalize_color(word)
            if normalized != word:
                detected_colors.append({
                    "original": word,
                    "normalized": normalized,
                    "category": "color"
                })
        
        return detected_colors
    
    async def suggest_color_normalization(self, color_text: str) -> List[Dict]:
        """색상 정규화 제안"""
        if not self.is_initialized:
            await self.initialize()
        
        return await self.mapping_system.suggest_normalization(color_text, "colors")
