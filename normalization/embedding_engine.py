#!/usr/bin/env python3
"""
임베딩 기반 텍스트 정규화 엔진
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
import json
import os
from utils import get_logger

logger = get_logger(__name__)

class EmbeddingNormalizationEngine:
    """임베딩 기반 정규화 엔진"""
    
    def __init__(self, model_name: str = "jhgan/ko-sroberta-multitask", threshold: float = 0.8):
        self.model_name = model_name
        self.threshold = threshold
        self.model = None
        self.device = "cpu"
        self.is_initialized = False
        
    async def initialize(self):
        """모델 초기화"""
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(self.model_name)
        self.model.to(self.device)
        self.is_initialized = True
        logger.info(f"임베딩 엔진 초기화 완료: {self.model_name}")
    
    async def get_embeddings(self, texts: List[str]) -> np.ndarray:
        """텍스트 임베딩 생성"""
        if not self.is_initialized:
            await self.initialize()
        
        if not texts:
            return np.array([])
        
        if self.model is None:
            return self._mock_embeddings(texts)
        
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings
    
    def _mock_embeddings(self, texts: List[str]) -> np.ndarray:
        """Mock 임베딩 (개발용)"""
        embeddings = []
        for text in texts:
            text_hash = hash(text) % 10000
            np.random.seed(text_hash)
            vector = np.random.normal(0, 1, 384)
            vector = vector / np.linalg.norm(vector)
            embeddings.append(vector)
        return np.array(embeddings)
    
    async def find_similar_terms(self, query_term: str, candidate_terms: List[str]) -> List[Tuple[str, float]]:
        """유사한 용어 찾기"""
        all_texts = [query_term] + candidate_terms
        embeddings = await self.get_embeddings(all_texts)
        
        query_embedding = embeddings[0:1]
        candidate_embeddings = embeddings[1:]
        
        similarities = np.dot(candidate_embeddings, query_embedding.T).flatten()
        
        similar_terms = []
        for i, similarity in enumerate(similarities):
            if similarity >= self.threshold:
                similar_terms.append((candidate_terms[i], float(similarity)))
        
        return sorted(similar_terms, key=lambda x: x[1], reverse=True)
    
    async def compute_similarity(self, text1: str, text2: str) -> float:
        """두 텍스트 간 유사도 계산"""
        embeddings = await self.get_embeddings([text1, text2])
        if embeddings.shape[0] < 2:
            return 0.0
        
        similarity = np.dot(embeddings[0], embeddings[1])
        return float(similarity)
