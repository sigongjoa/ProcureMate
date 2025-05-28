import os
from typing import Dict, Any

class ProcureMateSettings:
    """ProcureMate 전역 설정"""
    
    # Slack 설정
    SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
    SLACK_SIGNING_SECRET = os.getenv('SLACK_SIGNING_SECRET')
    SLACK_APP_TOKEN = os.getenv('SLACK_APP_TOKEN')
    
    # LLM 설정 (LM Studio)
    LLM_MODEL_NAME = "llambricks-horizon-ai-korean-llama-3.1-1ft-dpo-8b"
    LLM_SERVER_URL = "http://localhost:1234"
    LLM_MAX_TOKENS = 512
    LLM_TEMPERATURE = 0.7
    
    # 데이터베이스 설정
    VECTOR_DB_TYPE = "chroma"  # chroma or weaviate
    VECTOR_DB_HOST = "localhost"
    VECTOR_DB_PORT = 8000
    
    # API 설정
    COUPANG_ACCESS_KEY = os.getenv('COUPANG_ACCESS_KEY')
    COUPANG_SECRET_KEY = os.getenv('COUPANG_SECRET_KEY')
    G2B_API_KEY = os.getenv('G2B_API_KEY')
    
    # 문서 설정
    DOCUMENT_OUTPUT_PATH = "./output"
    TEMPLATE_PATH = "./templates"
    
    # 로깅 설정
    LOG_LEVEL = "DEBUG"
    LOG_FORMAT = "json"
    
    # 테스트 설정
    TEST_MODE = False
    MOCK_RESPONSES = True
    
    @classmethod
    def get_all_settings(cls) -> Dict[str, Any]:
        """모든 설정 반환"""
        return {
            key: getattr(cls, key) 
            for key in dir(cls) 
            if not key.startswith('_') and not callable(getattr(cls, key))
        }
    
    @classmethod
    def validate_required_settings(cls) -> bool:
        """필수 설정 검증"""
        required = [
            'SLACK_BOT_TOKEN',
            'SLACK_SIGNING_SECRET'
        ]
        
        missing = []
        for setting in required:
            if not getattr(cls, setting):
                missing.append(setting)
        
        if missing:
            raise ValueError(f"Missing required settings: {missing}")
        
        return True
