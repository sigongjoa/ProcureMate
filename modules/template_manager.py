"""
TemplateManager - 템플릿 파일 관리 모듈  
D:\procuremate\templates\ 폴더 기반 템플릿 저장/로드
"""
import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class TemplateManager:
    def __init__(self, templates_dir: str = None):
        if templates_dir is None:
            # 프로젝트 루트에서 templates 폴더 사용
            project_root = Path(__file__).parent.parent
            templates_dir = project_root / "templates"
        
        self.templates_dir = Path(templates_dir)
        self.document_templates_dir = self.templates_dir / "documents"
        self.settings_templates_dir = self.templates_dir / "settings"
        
        # 디렉토리 생성
        self.document_templates_dir.mkdir(parents=True, exist_ok=True)
        self.settings_templates_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"TemplateManager initialized: {self.templates_dir}")

    def save_document_template(self, name: str, template_data: Dict[str, Any]) -> bool:
        """문서 템플릿 저장"""
        try:
            template_file = self.document_templates_dir / f"{name}.json"
            
            # 메타데이터 추가
            template_data['metadata'] = {
                'created_at': datetime.now().isoformat(),
                'template_type': 'document',
                'version': '1.0'
            }
            
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Document template saved: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save document template {name}: {str(e)}", exc_info=True)
            return False

    def load_document_template(self, name: str) -> Optional[Dict[str, Any]]:
        """문서 템플릿 로드"""
        try:
            template_file = self.document_templates_dir / f"{name}.json"
            
            if not template_file.exists():
                logger.warning(f"Document template not found: {name}")
                return None
            
            with open(template_file, 'r', encoding='utf-8') as f:
                template_data = json.load(f)
            
            logger.info(f"Document template loaded: {name}")
            return template_data
            
        except Exception as e:
            logger.error(f"Failed to load document template {name}: {str(e)}", exc_info=True)
            return None

    def list_document_templates(self) -> Dict[str, Dict[str, Any]]:
        """문서 템플릿 목록 조회"""
        templates = {}
        
        try:
            if not self.document_templates_dir.exists():
                return templates
                
            for template_file in self.document_templates_dir.glob("*.json"):
                template_name = template_file.stem
                template_data = self.load_document_template(template_name)
                
                if template_data:
                    templates[template_name] = template_data
            
            logger.info(f"Listed {len(templates)} document templates")
            return templates
            
        except Exception as e:
            logger.error(f"Failed to list document templates: {str(e)}", exc_info=True)
            return {}

    def delete_document_template(self, name: str) -> bool:
        """문서 템플릿 삭제"""
        try:
            template_file = self.document_templates_dir / f"{name}.json"
            
            if template_file.exists():
                template_file.unlink()
                logger.info(f"Document template deleted: {name}")
                return True
            else:
                logger.warning(f"Document template not found for deletion: {name}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete document template {name}: {str(e)}", exc_info=True)
            return False

    def save_settings_template(self, name: str, settings_data: Dict[str, Any]) -> bool:
        """설정 템플릿 저장"""
        try:
            template_file = self.settings_templates_dir / f"{name}.json"
            
            # 메타데이터 추가
            settings_data['metadata'] = {
                'created_at': datetime.now().isoformat(),
                'template_type': 'settings',
                'version': '1.0'
            }
            
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(settings_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Settings template saved: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save settings template {name}: {str(e)}", exc_info=True)
            return False

    def list_settings_templates(self) -> Dict[str, Dict[str, Any]]:
        """설정 템플릿 목록 조회"""
        templates = {}
        
        try:
            if not self.settings_templates_dir.exists():
                return templates
                
            for template_file in self.settings_templates_dir.glob("*.json"):
                template_name = template_file.stem
                with open(template_file, 'r', encoding='utf-8') as f:
                    template_data = json.load(f)
                    templates[template_name] = template_data
            
            logger.info(f"Listed {len(templates)} settings templates")
            return templates
            
        except Exception as e:
            logger.error(f"Failed to list settings templates: {str(e)}", exc_info=True)
            return {}

# 전역 인스턴스
_template_manager = None

def get_template_manager():
    """글로벌 템플릿 매니저 인스턴스 반환"""
    global _template_manager
    if _template_manager is None:
        _template_manager = TemplateManager()
    return _template_manager
