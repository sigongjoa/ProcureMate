# 새 모듈 테스트 가이드

## 📋 테스트 개요

구현된 6개 새 모듈에 대한 테스트 코드:
- G2B API 클라이언트 테스트
- 쿠팡 API 클라이언트 테스트  
- 데이터 전처리 시스템 테스트
- 고급 RAG 시스템 테스트
- 자동 문서 생성 시스템 테스트
- API 핸들러 확장 테스트
- 전체 통합 테스트

## 🚀 빠른 테스트 실행

### 모든 테스트 실행
```bash
cd tests
python run_new_tests.py
```

### 특정 모듈 테스트만 실행
```bash
cd tests
python run_new_tests.py g2b_api          # G2B API 테스트
python run_new_tests.py coupang_api      # 쿠팡 API 테스트
python run_new_tests.py data_processor   # 데이터 전처리 테스트
python run_new_tests.py advanced_rag     # 고급 RAG 테스트
python run_new_tests.py document_generator # 문서 생성 테스트
python run_new_tests.py api_handlers     # API 핸들러 테스트
python run_new_tests.py integration      # 통합 테스트
```

## 🔧 수동 테스트 방법

### 1. pytest 직접 실행
```bash
cd tests
pytest test_g2b_api.py -v
pytest test_coupang_api.py -v
```

### 2. 개별 테스트 클래스 실행
```bash
pytest test_g2b_api.py::TestG2BAPIClient::test_client_initialization -v
```

### 3. 비동기 테스트 실행
```bash
pytest test_advanced_rag.py -v --asyncio-mode=auto
```

## 📊 테스트 결과 해석

### 성공 예시
```
✅ test_g2b_api.py: 통과
DEBUG: G2B 클라이언트 초기화 성공
DEBUG: 입찰공고 검색 결과: 5건
```

### 실패 예시  
```
❌ test_coupang_api.py: FAIL
ERROR: HMAC 서명 생성 실패
```

## ⚙️ 환경 설정

### 필수 환경 변수 (.env 파일)
```
G2B_SERVICE_KEY=your_g2b_api_key
COUPANG_ACCESS_KEY=your_coupang_access_key
COUPANG_SECRET_KEY=your_coupang_secret_key
COUPANG_VENDOR_ID=your_vendor_id
```

### 테스트 의존성 설치
```bash
pip install pytest>=7.0.0 pytest-asyncio>=0.21.0 pytest-mock>=3.10.0
```

## 🐛 문제 해결

### 자주 발생하는 오류

1. **모듈 임포트 오류**
   - `sys.path.append`로 경로 추가 확인
   - PYTHONPATH 환경 변수 설정

2. **비동기 테스트 오류**
   - `pytest-asyncio` 설치 확인
   - `@pytest.mark.asyncio` 데코레이터 확인

3. **API 테스트 실패**
   - 환경 변수 설정 확인
   - 네트워크 연결 상태 확인
   - API 키 유효성 확인

4. **한국어 처리 오류**
   - `konlpy` 패키지 설치 확인
   - Java 환경 설정 확인

## 📝 테스트 추가 방법

새 테스트 함수 작성 예시:
```python
def test_new_feature(self):
    try:
        # 테스트 로직
        result = some_function()
        assert result is not None
        print("DEBUG: 새 기능 테스트 통과")
    except Exception as e:
        print(f"ERROR: {str(e)}")
        raise
```

## 🔍 디버깅 팁

- 모든 테스트에서 `print("DEBUG: ...")` 로 진행 상황 출력
- 에러 발생 시 `print(f"ERROR: {str(e)}")` 로 스택 트레이스 출력
- `--capture=no` 옵션으로 print 출력 확인
- `-v` 옵션으로 상세 정보 확인
