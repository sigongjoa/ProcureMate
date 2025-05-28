import requests
import json
from typing import Dict, Any, List, Optional
from utils import get_logger, ModuleValidator, prompt_loader
from config import ProcureMateSettings

logger = get_logger(__name__)

class LlmModule:
    """한국어 LLM 통합 모듈"""
    
    def __init__(self):
        self.model_name = ProcureMateSettings.LLM_MODEL_NAME
        self.server_url = ProcureMateSettings.LLM_SERVER_URL
        self.max_tokens = ProcureMateSettings.LLM_MAX_TOKENS
        self.temperature = ProcureMateSettings.LLM_TEMPERATURE
        self.validator = ModuleValidator("LlmModule")
        
        logger.info("LlmModule 초기화")
    
    def generate_completion(self, prompt: str, max_tokens: Optional[int] = None) -> str:
        """텍스트 완성 생성"""
        if not self.check_server_health():
            raise Exception("채팅용 모델이 LM Studio에 로드되지 않았습니다.")
        
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens or self.max_tokens,
            "temperature": self.temperature,
            "stream": False
        }
        
        logger.debug(f"LLM 요청: {prompt[:100]}...")
        
        response = requests.post(
            f"{self.server_url}/v1/chat/completions",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        logger.debug(f"응답 상태: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            completion = result["choices"][0]["message"]["content"].strip()
            logger.debug(f"LLM 응답: {completion[:100]}...")
            return completion
        else:
            logger.error(f"LLM API 오류: {response.status_code} - {response.text}")
            if response.status_code == 404:
                raise Exception("채팅용 모델이 LM Studio에 로드되지 않았습니다.")
            else:
                raise Exception(f"LLM API 오류: {response.status_code}")

    def analyze_procurement_request(self, user_request: str) -> Dict[str, Any]:
        """조달 요청 분석"""
        try:
            prompt_template = prompt_loader.get_prompt("llm_prompts", "analyze_procurement_request")
            prompt = prompt_template.format(user_request=user_request)
        except KeyError as e:
            logger.error(f"프롬프트 템플릿 포맷팅 에러: {e}")
            # 기본 프롬프트 사용
            prompt = f"""다음 조달 요청을 분석하여 JSON 형태로 응답해주세요.

요청 내용: {user_request}

분석할 항목:
1. 필요한 물품 목록 (items)
2. 각 물품의 수량 (quantities)
3. 긴급도 (urgency: 높음/보통/낮음)
4. 예산 범위 (budget_range)
5. 특별 요구사항 (special_requirements)

응답 형식:
{{
  "items": ["물품1", "물품2"],
  "quantities": ["수량1", "수량2"],
  "urgency": "보통",
  "budget_range": "예산 범위",
  "special_requirements": ["요구사항1", "요구사항2"]
}}"""

        response = self.generate_completion(prompt)
        
        if response and '{' in response:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            json_str = response[json_start:json_end]
            
            result = json.loads(json_str)
            logger.info(f"조달 요청 분석 완료: {result}")
            return result
        else:
            logger.error("LLM 응답에서 JSON 형식을 찾을 수 없음")
            raise Exception("LLM 응답 파싱 실패: JSON 형식을 찾을 수 없음")

    def generate_procurement_recommendation(self, analysis: Dict[str, Any]) -> str:
        """조달 추천 생성"""
        items = ", ".join(analysis.get("items", []))
        quantities = analysis.get('quantities', [])
        urgency = analysis.get('urgency', '보통')
        budget_range = analysis.get('budget_range', '미정')
        
        try:
            prompt_template = prompt_loader.get_prompt("llm_prompts", "generate_procurement_recommendation")
            prompt = prompt_template.format(
                items=items,
                quantities=quantities,
                urgency=urgency,
                budget_range=budget_range
            )
        except KeyError as e:
            logger.error(f"프롬프트 템플릿 포맷팅 에러: {e}")
            # 기본 프롬프트 사용
            prompt = f"""다음 조달 분석 결과를 바탕으로 구매 추천을 생성해주세요.

필요 물품: {items}
수량: {quantities}
긴급도: {urgency}
예산 범위: {budget_range}

추천 내용:
1. 구매 우선순위
2. 예산 최적화 방안
3. 공급업체 선정 기준
4. 납기 관리 방안
5. 품질 확보 방안

한국어로 상세하고 실용적인 추천을 제공해주세요."""
        
        recommendation = self.generate_completion(prompt, max_tokens=300)
        
        if not recommendation:
            raise Exception("LLM 추천 생성 실패: 응답이 비어있음")
        
        logger.info("조달 추천 생성 완료")
        return recommendation
    
    def check_server_health(self) -> bool:
        """채팅 모델 확인 및 모델명 업데이트"""
        try:
            response = requests.get(f"{self.server_url}/v1/models", timeout=5)
            
            if response.status_code == 200:
                models = response.json()
                if models.get('data') and len(models['data']) > 0:
                    model_names = [model['id'] for model in models['data']]
                    logger.info(f"로드된 모델: {model_names}")
                    
                    # 채팅 완료용 모델 확인 (임베딩 모델 제외)
                    chat_models = [m for m in model_names if 'embedding' not in m.lower()]
                    if chat_models:
                        logger.info(f"채팅용 모델 발견: {chat_models}")
                        self.model_name = chat_models[0]
                        return True
                    else:
                        logger.error(f"채팅용 모델 없음. 임베딩 모델만 로드됨: {model_names}")
                        return False
                else:
                    logger.error("LLM 서버 연결됨 하지만 모델 없음")
                    return False
            else:
                logger.error(f"LLM 서버 상태 이상: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"LLM 서버 체크 실패: {e}")
            return False

    def run_validation_tests(self) -> bool:
        """모듈 검증 테스트"""
        test_cases = [
            {
                "input": {"user_request": "사무용 의자 5개 필요"},
                "expected": None
            }
        ]
        
        def test_analysis(user_request: str):
            result = self.analyze_procurement_request(user_request)
            return isinstance(result, dict) and "items" in result
        
        validation_result = self.validator.validate_function(test_analysis, test_cases)
        server_ok = self.check_server_health()
        
        debug_info = self.validator.debug_module_state(self)
        summary = self.validator.get_test_summary()
        
        logger.info(f"LlmModule validation summary: {summary}")
        logger.info(f"Server health: {server_ok}")
        
        return validation_result and server_ok

if __name__ == "__main__":
    logger.info("LlmModule 디버그 모드 시작")
    
    llm = LlmModule()
    
    if llm.check_server_health():
        logger.info("LLM 서버 연결 성공")
        
        test_request = "사무용 책상 2개와 의자 2개 필요합니다"
        analysis = llm.analyze_procurement_request(test_request)
        logger.info(f"분석 결과: {analysis}")
        
        recommendation = llm.generate_procurement_recommendation(analysis)
        logger.info(f"추천: {recommendation}")
    else:
        logger.error("LLM 서버 연결 실패")
        raise Exception("LLM 서버 연결 실패")
    
    if llm.run_validation_tests():
        logger.info("모든 검증 테스트 통과")
    else:
        logger.error("검증 테스트 실패")
    
    logger.info("LlmModule 디버그 완료")
