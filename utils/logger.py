import logging
import json
import traceback
from datetime import datetime
from typing import Any, Dict

class ProcureMateLogger:
    """ERROR 레벨 스택트레이스 직접 출력, JSON 포맷 로깅"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        
        if not self.logger.handlers:
            self.logger.addHandler(handler)
    
    def _format_log(self, level: str, message: str, trace: str = None) -> str:
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
            "trace": trace
        }
        return json.dumps(log_data, ensure_ascii=False)
    
    def debug(self, message: str):
        self.logger.debug(self._format_log("DEBUG", message))
    
    def info(self, message: str):
        self.logger.info(self._format_log("INFO", message))
    
    def warning(self, message: str):
        self.logger.warning(self._format_log("WARNING", message))
    
    def error(self, message: str):
        # 스택트레이스 그대로 출력
        trace = traceback.format_exc()
        self.logger.error(self._format_log("ERROR", message, trace))

def get_logger(name: str) -> ProcureMateLogger:
    return ProcureMateLogger(name)
