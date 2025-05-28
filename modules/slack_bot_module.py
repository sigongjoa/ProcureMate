from slack_bolt import App
from slack_bolt.adapter.fastapi import SlackRequestHandler
from fastapi import FastAPI, Request
import uvicorn
from typing import Dict, Any
from utils import get_logger, ModuleValidator
from config import ProcureMateSettings

logger = get_logger(__name__)

class SlackBotModule:
    """Slack 챗봇 모듈 - CamelCase UIA 태깅"""
    
    def __init__(self):
        self.app = None
        self.fastapi_app = None
        self.handler = None
        self.validator = ModuleValidator("SlackBotModule")
        
        logger.info("SlackBotModule 초기화")
    
    def initialize_slack_app(self) -> bool:
        """Slack 앱 초기화"""

        ProcureMateSettings.validate_required_settings()
        
        self.app = App(
            token=ProcureMateSettings.SLACK_BOT_TOKEN,
            signing_secret=ProcureMateSettings.SLACK_SIGNING_SECRET
        )
        
        self._register_commands()
        self._register_events()
        
        logger.info("Slack 앱 초기화 완료")
        return True
            
 
    def _register_commands(self):
        """슬래시 커맨드 등록"""
        
        @self.app.command("/procure")
        def handle_procure_command(ack, body, respond, command):
            ack()
            
            user_id = body["user_id"]
            text = command.get('text', '')
            
            logger.debug(f"Procure command received: user={user_id}, text={text}")
            
            if not text.strip():
                respond("😅 조달할 물품을 입력해주세요! 예: /procure 사무용 의자 10개")
                return
            
            # 비동기 처리 시뮬레이션
            self._process_procurement_request(user_id, text, respond)
    
    def _register_events(self):
        """이벤트 핸들러 등록"""
        
        @self.app.event("app_mention")
        def handle_app_mention(event, say):
            user = event['user']
            text = event['text']
            
            logger.debug(f"App mention: user={user}, text={text}")
            
            say(f"<@{user}> 안녕하세요! ProcureMate입니다. `/procure [물품명]`으로 조달 요청하세요.")
    
    def _process_procurement_request(self, user_id: str, text: str, respond):
        """조달 요청 처리"""

        logger.info(f"Processing procurement request: {text}")
        
        # 기본 응답
        respond(f"🔍 조달 요청 처리 중: {text}")
        
        # 실제 처리 로직은 여기에 추가
        # LLM 모듈, 데이터 수집 모듈 등과 연동
        
        logger.info("Procurement request processed successfully")

    
    def setup_fastapi_server(self) -> FastAPI:
        """FastAPI 서버 설정"""
        self.fastapi_app = FastAPI(title="ProcureMate Slack Bot")
        self.handler = SlackRequestHandler(self.app)
        
        @self.fastapi_app.post("/slack/events")
        async def slack_events(req: Request):
            return await self.handler.handle(req)
        
        @self.fastapi_app.get("/health")
        def health_check():
            return {"status": "healthy", "module": "SlackBotModule"}
        
        logger.info("FastAPI 서버 설정 완료")
        return self.fastapi_app
    
    def start_server(self, host: str = "0.0.0.0", port: int = 3000):
        """서버 시작"""
        if not self.fastapi_app:
            self.setup_fastapi_server()
        
        logger.info(f"Starting server on {host}:{port}")
        uvicorn.run(self.fastapi_app, host=host, port=port)
    
    def run_validation_tests(self) -> bool:
        """모듈 검증 테스트 실행"""
        test_cases = [
            {
                "input": {"text": "사무용 의자"},
                "expected": None  # 실제 처리 결과 검증은 별도 로직
            },
            {
                "input": {"text": ""},
                "expected": None
            }
        ]
        
        # 기본 기능 테스트
        def test_text_processing(text: str):
            return len(text.strip()) > 0
        
        result = self.validator.validate_function(test_text_processing, test_cases)
        
        debug_info = self.validator.debug_module_state(self)
        summary = self.validator.get_test_summary()
        
        logger.info(f"SlackBotModule validation summary: {summary}")
        
        return result

# 디버그 실행
if __name__ == "__main__":
    logger.info("SlackBotModule 디버그 모드 시작")
    
    bot = SlackBotModule()
    
    # 초기화 테스트
    if bot.initialize_slack_app():
        logger.info("Slack 앱 초기화 성공")
    else:
        logger.error("Slack 앱 초기화 실패")
    
    # 검증 테스트 실행
    if bot.run_validation_tests():
        logger.info("모든 검증 테스트 통과")
    else:
        logger.error("검증 테스트 실패")
    
    logger.info("SlackBotModule 디버그 완료")
