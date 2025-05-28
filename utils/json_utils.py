#!/usr/bin/env python3
"""
JSON 직렬화 유틸리티
"""

from datetime import datetime
from typing import Any, Dict
import json

def datetime_serializer(obj: Any) -> str:
    """datetime 객체를 ISO 문자열로 변환"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

def safe_json_dumps(data: Any) -> str:
    """안전한 JSON 직렬화"""
    return json.dumps(data, default=datetime_serializer, ensure_ascii=False)

def serialize_for_websocket(data: Dict[str, Any]) -> Dict[str, Any]:
    """WebSocket 전송용 데이터 직렬화"""
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, dict):
                result[key] = serialize_for_websocket(value)
            elif isinstance(value, list):
                result[key] = [serialize_for_websocket(item) if isinstance(item, dict) else 
                              item.isoformat() if isinstance(item, datetime) else item 
                              for item in value]
            else:
                result[key] = value
        return result
    return data
