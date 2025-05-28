#!/usr/bin/env python3
"""
임베딩 기반 유사어 매핑 시스템
"""

import json
import asyncio
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
from .embedding_engine import EmbeddingNormalizationEngine
from utils import get_logger

logger = get_logger(__name__)

@dataclass
class NormalizationRule:
    """정규화 규칙"""
    standard_term: str
    variants: List[str]
    category: str
    confidence: float
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'NormalizationRule':
        return cls(**data)

class SimilarityMappingSystem:
    """임베딩 기반 유사어 매핑"""
    
    def __init__(self, rules_file: str = "normalization_rules.json"):
        self.engine = EmbeddingNormalizationEngine()
        self.rules_file = rules_file
        self.rules: Dict[str, List[NormalizationRule]] = {}
        self.standard_terms: Dict[str, Set[str]] = {}
    
    async def initialize(self):
        """시스템 초기화"""
        await self.engine.initialize()
        await self.load_rules()
        logger.info("유사어 매핑 시스템 초기화 완료")
    
    async def load_rules(self):
        """규칙 파일 로드"""
        try:
            with open(self.rules_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for category, rules_data in data.items():
                self.rules[category] = [NormalizationRule.from_dict(rule) for rule in rules_data]
                self.standard_terms[category] = set()
                
                for rule in self.rules[category]:
                    self.standard_terms[category].add(rule.standard_term)
            
            logger.info(f"규칙 로드 완료: {len(self.rules)} 카테고리")
            
        except FileNotFoundError:
            logger.info("규칙 파일 없음, 기본 규칙으로 초기화")
            await self._create_default_rules()
    
    async def _create_default_rules(self):
        """기본 규칙 생성"""
        default_rules = {
            "colors": [
                {
                    "standard_term": "흰색",
                    "variants": ["화이트", "white", "WHITE", "백색", "하얀색"],
                    "category": "colors",
                    "confidence": 0.9
                },
                {
                    "standard_term": "검은색",
                    "variants": ["블랙", "black", "BLACK", "흑색", "까만색"],
                    "category": "colors",
                    "confidence": 0.9
                },
                {
                    "standard_term": "파란색",
                    "variants": ["블루", "blue", "BLUE", "청색"],
                    "category": "colors",
                    "confidence": 0.9
                }
            ],
            "brands": [
                {
                    "standard_term": "삼성",
                    "variants": ["Samsung", "SAMSUNG", "삼성전자"],
                    "category": "brands",
                    "confidence": 0.95
                },
                {
                    "standard_term": "엘지",
                    "variants": ["LG", "엘지전자", "LG전자"],
                    "category": "brands",
                    "confidence": 0.95
                }
            ],
            "units": [
                {
                    "standard_term": "개",
                    "variants": ["EA", "ea", "대", "매", "장"],
                    "category": "units",
                    "confidence": 0.85
                }
            ]
        }
        
        self.rules = {}
        self.standard_terms = {}
        
        for category, rules_data in default_rules.items():
            self.rules[category] = [NormalizationRule.from_dict(rule) for rule in rules_data]
            self.standard_terms[category] = {rule["standard_term"] for rule in rules_data}
        
        await self.save_rules()
    
    async def save_rules(self):
        """규칙 저장"""
        data = {}
        for category, rules in self.rules.items():
            data[category] = [rule.to_dict() for rule in rules]
        
        with open(self.rules_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info("규칙 저장 완료")
    
    async def normalize_term(self, term: str, category: Optional[str] = None) -> str:
        """용어 정규화"""
        if not term.strip():
            return term
        
        categories_to_check = [category] if category else self.rules.keys()
        
        for cat in categories_to_check:
            if cat not in self.rules:
                continue
            
            # 정확한 매칭 우선
            for rule in self.rules[cat]:
                if term in rule.variants or term == rule.standard_term:
                    return rule.standard_term
            
            # 임베딩 기반 유사도 매칭
            best_match = await self._find_best_embedding_match(term, cat)
            if best_match:
                return best_match
        
        return term
    
    async def _find_best_embedding_match(self, term: str, category: str) -> Optional[str]:
        """임베딩 기반 최적 매칭"""
        if category not in self.rules:
            return None
        
        all_variants = []
        variant_to_standard = {}
        
        for rule in self.rules[category]:
            for variant in rule.variants + [rule.standard_term]:
                all_variants.append(variant)
                variant_to_standard[variant] = rule.standard_term
        
        similar_terms = await self.engine.find_similar_terms(term, all_variants)
        
        if similar_terms and similar_terms[0][1] >= self.engine.threshold:
            best_variant = similar_terms[0][0]
            return variant_to_standard[best_variant]
        
        return None
    
    async def add_new_variant(self, standard_term: str, new_variant: str, category: str, confidence: float = 0.8):
        """새로운 변형 추가"""
        if category not in self.rules:
            self.rules[category] = []
            self.standard_terms[category] = set()
        
        # 기존 규칙에 추가
        for rule in self.rules[category]:
            if rule.standard_term == standard_term:
                if new_variant not in rule.variants:
                    rule.variants.append(new_variant)
                    await self.save_rules()
                    logger.info(f"변형 추가: {new_variant} -> {standard_term}")
                return
        
        # 새 규칙 생성
        new_rule = NormalizationRule(
            standard_term=standard_term,
            variants=[new_variant],
            category=category,
            confidence=confidence
        )
        self.rules[category].append(new_rule)
        self.standard_terms[category].add(standard_term)
        await self.save_rules()
        logger.info(f"새 규칙 생성: {new_variant} -> {standard_term}")
    
    async def suggest_normalization(self, term: str, category: Optional[str] = None) -> List[Dict]:
        """정규화 제안"""
        suggestions = []
        categories_to_check = [category] if category else self.rules.keys()
        
        for cat in categories_to_check:
            if cat not in self.rules:
                continue
            
            all_variants = []
            for rule in self.rules[cat]:
                all_variants.extend(rule.variants + [rule.standard_term])
            
            similar_terms = await self.engine.find_similar_terms(term, all_variants)
            
            for similar_term, similarity in similar_terms[:3]:
                # 해당 변형이 속한 표준 용어 찾기
                for rule in self.rules[cat]:
                    if similar_term in rule.variants or similar_term == rule.standard_term:
                        suggestions.append({
                            "original": term,
                            "suggested": rule.standard_term,
                            "category": cat,
                            "similarity": similarity,
                            "matched_variant": similar_term
                        })
                        break
        
        return sorted(suggestions, key=lambda x: x["similarity"], reverse=True)
