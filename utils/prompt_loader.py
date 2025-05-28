#!/usr/bin/env python3
"""
프롬프트 로더 - 프롬프트와 템플릿 관리
"""

import json
from pathlib import Path
from typing import Dict, Any
from utils import get_logger

logger = get_logger(__name__)

class PromptLoader:
    """프롬프트 및 템플릿 로더"""
    
    def __init__(self):
        self.prompts_dir = Path(__file__).parent.parent / "prompts"
        self._cache = {}
        
    def load_prompts(self, prompt_file: str) -> Dict[str, str]:
        """프롬프트 파일 로드"""
        if prompt_file in self._cache:
            return self._cache[prompt_file]
            
        prompt_path = self.prompts_dir / f"{prompt_file}.json"
        
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                prompts = json.load(f)
            
            self._cache[prompt_file] = prompts
            logger.debug(f"프롬프트 로드: {prompt_file}")
            return prompts
            
        except Exception as e:
            logger.error(f"프롬프트 로드 실패: {prompt_file} - {e}")
            return {}
    
    def get_prompt(self, prompt_file: str, prompt_name: str) -> str:
        """특정 프롬프트 가져오기"""
        prompts = self.load_prompts(prompt_file)
        return prompts.get(prompt_name, "")
    
    def save_prompt(self, prompt_file: str, prompt_name: str, template: str) -> bool:
        """프롬프트 저장"""
        try:
            # 현재 프롬프트 로드
            prompts = self.load_prompts(prompt_file)
            
            # 새 프롬프트 추가/업데이트
            prompts[prompt_name] = template
            
            # 파일에 저장
            prompt_path = self.prompts_dir / f"{prompt_file}.json"
            prompt_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(prompt_path, 'w', encoding='utf-8') as f:
                json.dump(prompts, f, ensure_ascii=False, indent=2)
            
            # 캐시 업데이트
            self._cache[prompt_file] = prompts
            
            logger.info(f"프롬프트 저장 완료: {prompt_file}.{prompt_name}")
            return True
            
        except Exception as e:
            logger.error(f"프롬프트 저장 실패: {prompt_file}.{prompt_name} - {e}")
            return False
    
    def get_available_prompts(self, prompt_file: str) -> list:
        """사용 가능한 프롬프트 목록 반환"""
        prompts = self.load_prompts(prompt_file)
        return list(prompts.keys())
    
    def load_template(self, template_name: str) -> str:
        """HTML 템플릿 로드"""
        template_path = self.prompts_dir / "templates" / template_name
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"템플릿 로드 실패: {template_name} - {e}")
            return ""

# 전역 인스턴스
prompt_loader = PromptLoader()

def get_prompt_loader() -> PromptLoader:
    """전역 프롬프트 로더 인스턴스 반환"""
    return prompt_loader
