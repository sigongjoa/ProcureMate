# 성능 메트릭 하드코딩 오류 수정

## 문제 상황
- GUI에서 LLM 테스트 결과의 성능 메트릭이 X로 표시됨
- 품질점수, 수량감지, JSON 유효성 등이 제대로 표시되지 않음

## 원인 분석
`handlers.py`에서 메트릭을 `additional_metrics` 필드에 저장하는데
HTML 템플릿에서는 직접 접근하려고 시도함

**기존 코드 (handlers.py):**
```python
additional_metrics={
    "has_items": len(analysis_result.get("items", [])) > 0,
    "has_quantities": len(analysis_result.get("quantities", [])) > 0,
    "json_valid": isinstance(analysis_result, dict),
    ...
}
```

**HTML 템플릿 (잘못된 접근):**
```javascript
metrics.has_items  // undefined
```

## 해결 방법
HTML 템플릿에서 올바른 경로로 접근하도록 수정

**수정된 HTML:**
```javascript
metrics.additional_metrics.has_items
metrics.additional_metrics.has_quantities  
metrics.additional_metrics.json_valid
```

## 수정 파일
- `/gui/templates/llm_test.html` 

## 결과
- 성능 메트릭이 정상적으로 ✅/❌로 표시됨
- JSON 유효성, 물품감지, 수량감지 상태 정확히 표시

## 수정 완료 시간
2025-05-28
