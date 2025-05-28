#!/usr/bin/env python3
"""
기존 시스템과 새로운 정규화 시스템 간 어댑터
"""

from typing import Dict, List
from normalization import UnifiedTextProcessor
from utils import get_logger

logger = get_logger(__name__)

class NormalizationAdapter:
    """정규화 시스템 어댑터"""
    
    def __init__(self):
        self.processor = UnifiedTextProcessor()
        self.is_initialized = False
    
    async def initialize(self):
        """어댑터 초기화"""
        await self.processor.initialize()
        self.is_initialized = True
        logger.info("정규화 어댑터 초기화 완료")
    
    async def replace_korean_text_normalizer(self, text: str) -> Dict[str, str]:
        """기존 KoreanTextNormalizer.normalize_text() 대체"""
        if not self.is_initialized:
            await self.initialize()
        
        return await self.processor.process_text(text)
    
    async def migrate_data_processor(self):
        """data_processor.py 마이그레이션 도움"""
        logger.info("data_processor.py 마이그레이션 가이드:")
        logger.info("1. KoreanTextNormalizer 클래스를 NormalizationAdapter로 교체")
        logger.info("2. normalize_text() 메서드를 replace_korean_text_normalizer()로 교체")
        logger.info("3. 하드코딩된 매핑 딕셔너리들 제거")
        
        return {
            "old_class": "KoreanTextNormalizer",
            "new_class": "NormalizationAdapter",
            "old_method": "normalize_text()",
            "new_method": "replace_korean_text_normalizer()",
            "migration_status": "ready"
        }
