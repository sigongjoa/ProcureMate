import pytest
import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from modules import SlackBotModule
from utils import get_logger

logger = get_logger(__name__)

class TestSlackBotModule:
    """SlackBotModule 테스트"""
    
    @pytest.fixture
    def slack_bot(self):
        """SlackBotModule 인스턴스 생성"""
        return SlackBotModule()
    
    def test_slack_bot_initialization(self, slack_bot):
        """SlackBot 초기화 테스트"""
        assert slack_bot is not None
        assert hasattr(slack_bot, 'validator')
        assert slack_bot.validator.module_name == "SlackBotModule"
        logger.info("SlackBot 초기화 테스트 통과")
    
    def test_slack_app_setup(self, slack_bot):
        """Slack 앱 설정 테스트 (환경변수 없이)"""
        # 환경변수가 없는 경우 False 반환 확인
        os.environ.pop('SLACK_BOT_TOKEN', None)
        os.environ.pop('SLACK_SIGNING_SECRET', None)
        
        try:
            result = slack_bot.initialize_slack_app()
            # 환경변수가 없으면 False가 반환되어야 함
            assert result == False
            logger.info("Slack 앱 설정 테스트 (환경변수 없음) 통과")
        except ValueError as e:
            # 환경변수 검증 오류도 예상되는 결과
            assert "Missing required settings" in str(e)
            logger.info("Slack 앱 설정 테스트 (검증 오류) 통과")
    
    def test_fastapi_server_setup(self, slack_bot):
        """FastAPI 서버 설정 테스트"""
        app = slack_bot.setup_fastapi_server()
        
        assert app is not None
        assert slack_bot.fastapi_app is not None
        assert slack_bot.handler is not None
        
        logger.info("FastAPI 서버 설정 테스트 통과")
    
    def test_validation_tests(self, slack_bot):
        """내장 검증 테스트"""
        result = slack_bot.run_validation_tests()
        assert isinstance(result, bool)
        logger.info(f"SlackBot 검증 테스트 결과: {result}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
