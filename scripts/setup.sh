#!/bin/bash

echo "🚀 ProcureMate 시스템 시작 스크립트"

# 환경 변수 확인
if [ ! -f .env ]; then
    echo "⚠️  .env 파일이 없습니다. .env.example을 복사하여 설정하세요."
    echo "   cp .env.example .env"
    exit 1
fi

# 가상환경 활성화 (있는 경우)
if [ -d "venv" ]; then
    echo "📦 가상환경 활성화"
    source venv/bin/activate
fi

# 의존성 설치
echo "📦 의존성 설치 중..."
pip install -r requirements.txt

# 필요한 디렉토리 생성
echo "📁 디렉토리 생성"
mkdir -p output templates test_reports chroma_db

# 권한 설정
chmod +x scripts/*.sh

echo "✅ 설정 완료"
echo ""
echo "다음 명령으로 시스템을 시작할 수 있습니다:"
echo "  python main.py              # 메인 시스템 실행"
echo "  python -m pytest tests/     # 테스트 실행"
echo "  docker-compose up           # Docker로 실행"
echo ""
