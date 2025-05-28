#!/bin/bash

echo "🧪 ProcureMate 테스트 실행"

# 가상환경 활성화 (있는 경우)
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# 테스트 디렉토리로 이동
cd "$(dirname "$0")/.."

# 단위 테스트 실행
echo "📋 단위 테스트 실행..."
python -m pytest tests/ -v --tb=short

# 커버리지 측정 (pytest-cov가 설치된 경우)
if pip list | grep pytest-cov > /dev/null; then
    echo ""
    echo "📊 커버리지 측정..."
    python -m pytest tests/ --cov=modules --cov-report=term-missing
fi

# 개별 모듈 디버그 실행
echo ""
echo "🔍 개별 모듈 디버그 테스트..."

echo "  - SlackBotModule"
python modules/slack_bot_module.py

echo "  - LlmModule"
python modules/llm_module.py

echo "  - DataCollectorModule"
python modules/data_collector_module.py

echo "  - VectorDbModule"
python modules/vector_db_module.py

echo "  - DocumentAutomationModule"
python modules/document_automation_module.py

echo "  - TestFrameworkModule"
python modules/test_framework_module.py

echo ""
echo "✅ 모든 테스트 완료"
