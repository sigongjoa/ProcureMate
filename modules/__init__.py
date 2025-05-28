#!/usr/bin/env python3
"""
ProcureMate 모듈 패키지
업데이트된 모듈들과 새로운 고급 기능들을 포함
"""

# 기존 모듈들
from .llm_module import LlmModule
from .vector_db_module import VectorDbModule
from .data_collector_module import DataCollectorModule
from .document_automation_module import DocumentAutomationModule
from .test_framework_module import TestFrameworkModule
from .slack_bot_module import SlackBotModule

# 새로운 고급 모듈들
from .g2b_api_client import G2BAPIClient
from .coupang_api_client import CoupangAuth, RateLimitedCoupangClient
# CoupangAPIClient는 RateLimitedCoupangClient의 별칭
CoupangAPIClient = RateLimitedCoupangClient
from .data_processor import (
    UnifiedProduct, 
    KoreanTextNormalizer, 
    DataIntegrator, 
    ProductDeduplicator
)
from .advanced_rag_module import (
    KoreanEmbeddingEngine,
    BM25Scorer,
    HybridSearchEngine,
    AdvancedVectorDbModule
)
# AdvancedRAGModule은 AdvancedVectorDbModule의 별칭
AdvancedRAGModule = AdvancedVectorDbModule
from .document_generator import (
    ProcurementRequirement,
    ProcurementDocumentGenerator
)
# DocumentGenerator는 ProcurementDocumentGenerator의 별칭
DocumentGenerator = ProcurementDocumentGenerator
from .document_form_generator import (
    DocumentFormField,
    DocumentTemplate,
    DocumentFormGenerator
)

__all__ = [
    # 기존 모듈
    'LlmModule',
    'VectorDbModule', 
    'DataCollectorModule',
    'DocumentAutomationModule',
    'TestFrameworkModule',
    'SlackBotModule',
    
    # 새로운 API 클라이언트
    'G2BAPIClient',
    'CoupangAuth',
    'RateLimitedCoupangClient',
    'CoupangAPIClient',
    
    # 데이터 처리
    'UnifiedProduct',
    'KoreanTextNormalizer',
    'DataIntegrator',
    'ProductDeduplicator',
    
    # 고급 RAG
    'KoreanEmbeddingEngine',
    'BM25Scorer', 
    'HybridSearchEngine',
    'AdvancedVectorDbModule',
    'AdvancedRAGModule',
    
    # 문서 생성
    'ProcurementRequirement',
    'ProcurementDocumentGenerator',
    'DocumentGenerator',
    
    # 문서 폼 생성
    'DocumentFormField',
    'DocumentTemplate',
    'DocumentFormGenerator'
]

__version__ = "1.1.0"
__description__ = "ProcureMate - 한국형 지능형 조달 시스템"
