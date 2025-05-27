#!/usr/bin/env python3
"""
LLM 응답 상세 조회 핸들러
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import json
from .handlers import get_status_handler
from utils import get_logger

logger = get_logger(__name__)

class LLMResponseHandler:
    """LLM 응답 상세 조회 핸들러"""
    
    def __init__(self):
        self.status_handler = get_status_handler()
    
    async def get_llm_responses(self, limit: int = 20) -> Dict[str, Any]:
        """최근 LLM 응답들 조회"""
        llm_tests = [
            test for test in self.status_handler.test_results 
            if test.test_type == "llm_analysis"
        ]
        
        llm_tests.sort(key=lambda x: x.timestamp, reverse=True)
        
        responses = []
        for test in llm_tests[:limit]:
            response_data = {
                "id": test.id,
                "timestamp": test.timestamp.isoformat(),
                "status": test.status,
                "input_query": test.input_data.get("query", ""),
                "llm_response": test.output_data,
                "response_time": test.metrics.response_time,
                "quality_score": test.metrics.quality_score,
                "error": test.error_message
            }
            responses.append(response_data)
        
        return {
            "responses": responses,
            "total": len(llm_tests),
            "limit": limit
        }

    
    async def get_llm_response_detail(self, test_id: str) -> Optional[Dict[str, Any]]:
        """특정 LLM 응답 상세 조회"""
        test = await self.status_handler.get_test_detail(test_id)
        
        if not test or test.test_type != "llm_analysis":
            return None
        
        return {
            "id": test.id,
            "timestamp": test.timestamp.isoformat(),
            "status": test.status,
            "duration": test.duration,
            "input_data": test.input_data,
            "output_data": test.output_data,
            "metrics": test.metrics.dict(),
            "error_message": test.error_message,
            "formatted_response": self._format_llm_response(test.output_data)
        }

    
    def _format_llm_response(self, response_data: Dict[str, Any]) -> str:
        """LLM 응답을 읽기 쉽게 포맷팅"""
        if not response_data:
            return "응답 없음"
        
        if isinstance(response_data, dict):
            formatted = "=== LLM 분석 결과 ===\n\n"
            
            if "items" in response_data:
                formatted += f"📦 요청 물품: {', '.join(response_data['items'])}\n"
            
            if "quantities" in response_data:
                formatted += f"📊 수량: {', '.join(response_data['quantities'])}\n"
            
            if "urgency" in response_data:
                formatted += f"⚡ 긴급도: {response_data['urgency']}\n"
            
            if "budget_range" in response_data:
                formatted += f"💰 예산 범위: {response_data['budget_range']}\n"
            
            if "specifications" in response_data and response_data['specifications']:
                formatted += f"📋 사양: {', '.join(response_data['specifications'])}\n"
            
            formatted += f"\n=== 원본 JSON ===\n{json.dumps(response_data, indent=2, ensure_ascii=False)}"
            return formatted
        
        return str(response_data)

def get_llm_response_handler() -> LLMResponseHandler:
    """LLM 응답 핸들러 싱글톤"""
    global _llm_response_handler
    if '_llm_response_handler' not in globals():
        globals()['_llm_response_handler'] = LLMResponseHandler()
    return globals()['_llm_response_handler']
