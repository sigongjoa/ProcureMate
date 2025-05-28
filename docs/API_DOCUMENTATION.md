# ProcureMate API 문서

**버전:** 1.0.0  
**최종 업데이트:** 2025-05-26  
**작성자:** ProcureMate 개발팀

## 📋 목차

1. [개요 및 시작하기](#개요-및-시작하기)
2. [환경 설정](#환경-설정)
3. [외부 API 연동](#외부-api-연동)
4. [Web GUI API](#web-gui-api)
5. [내부 모듈 API](#내부-모듈-api)
6. [사용 예시](#사용-예시)
7. [에러 처리](#에러-처리)
8. [FAQ](#faq)

---

## 🚀 개요 및 시작하기

ProcureMate는 한국형 지능형 조달 시스템으로, 다음과 같은 API들을 제공합니다:

### 주요 기능
- **외부 데이터 수집**: 쿠팡, G2B(나라장터) API 연동
- **AI 기반 분석**: LLM 및 RAG 시스템을 통한 지능형 분석
- **문서 자동화**: 조달 관련 문서 자동 생성
- **성능 모니터링**: 실시간 시스템 상태 및 성능 분석

### 서버 실행
```bash
# GUI 서버 시작 (포트 8080)
cd gui
python main.py

# 또는 uvicorn 직접 실행
uvicorn gui.main:app --host 0.0.0.0 --port 8080 --reload
```

### Base URL
```
http://localhost:8080
```

---

## ⚙️ 환경 설정

### 필수 환경 변수

`.env` 파일을 생성하여 다음 환경 변수들을 설정하세요:

```bash
# 쿠팡 API 설정
COUPANG_ACCESS_KEY=your_coupang_access_key
COUPANG_SECRET_KEY=your_coupang_secret_key
COUPANG_VENDOR_ID=your_vendor_id

# G2B API 설정 (공공데이터포털)
G2B_SERVICE_KEY=your_g2b_service_key

# LLM 서버 설정
LLM_SERVER_URL=http://localhost:11434
LLM_MODEL_NAME=llama2:7b
LLM_MAX_TOKENS=512
LLM_TEMPERATURE=0.7

# 벡터 DB 설정
VECTOR_DB_TYPE=chroma
VECTOR_DB_HOST=localhost
VECTOR_DB_PORT=8000
```

### Mock 모드
API 키가 설정되지 않은 경우, 시스템은 자동으로 Mock 데이터를 사용합니다.

---

## 🌐 외부 API 연동

### 1. 쿠팡 API

#### 인증 방식
- **HMAC SHA256** 서명 기반 인증
- Access Key, Secret Key, Vendor ID 필요

#### 사용 가능한 기능

##### 상품 검색
```python
from modules.coupang_api_client import CoupangAuth, RateLimitedCoupangClient

auth = CoupangAuth(access_key, secret_key, vendor_id)
async with RateLimitedCoupangClient(auth) as client:
    result = await client.search_products("사무용 책상", {
        'limit': 20,
        'min_price': 100000,
        'max_price': 1000000
    })
```

##### 상품 상세 조회
```python
product_detail = await client.get_product_details("product_id")
```

##### 카테고리 조회
```python
categories = await client.get_product_categories()
```

#### 응답 형식
```json
{
  "success": true,
  "total_count": 10,
  "items": [
    {
      "id": "coupang_12345",
      "name": "사무용 책상",
      "price": 450000,
      "original_price": 500000,
      "discount_rate": 10,
      "image_url": "https://...",
      "vendor_name": "판매자명",
      "rating": 4.5,
      "review_count": 100,
      "source": "coupang"
    }
  ]
}
```

### 2. G2B (나라장터) API

#### 인증 방식
- **공공데이터포털 API 키** 사용
- 별도 회원가입 및 API 신청 필요

#### 사용 가능한 기능

##### 입찰공고 조회
```python
from modules.g2b_api_client import G2BAPIClient

async with G2BAPIClient() as client:
    result = await client.get_bid_announcements({
        'limit': 100,
        'start_date': '20250520',
        'end_date': '20250527'
    })
```

##### 계약정보 조회
```python
contracts = await client.get_contract_info({'limit': 50})
```

##### 가격정보 조회
```python
prices = await client.get_price_info({
    'item_name': '사무용품',
    'year_month': '202505'
})
```

#### 응답 형식
```json
{
  "success": true,
  "total_count": 5,
  "items": [
    {
      "id": "g2b_bid_20250526001",
      "announcement_number": "20250526-001",
      "title": "사무용품 구매",
      "organization": "정부기관명",
      "budget": 5000000,
      "announcement_date": "20250526",
      "deadline": "20250610",
      "source": "g2b"
    }
  ]
}
```

---

## 🖥️ Web GUI API

모든 Web API는 `/api` 접두어를 사용합니다.

### 1. 시스템 관리

#### 시스템 상태 조회
```http
GET /api/system/status
```

**응답:**
```json
{
  "llm_connected": true,
  "vector_db_ready": true,
  "total_tests": 150,
  "last_test": "2025-05-26T13:30:00",
  "modules": {
    "llm": {"status": "healthy", "details": {}},
    "vector_db": {"status": "healthy", "details": {}}
  }
}
```

#### 헬스 체크
```http
GET /api/health
```

#### 시스템 설정 조회/업데이트
```http
GET /api/config
POST /api/config
```

### 2. LLM 테스트

#### LLM 분석 테스트
```http
POST /api/llm/test
Content-Type: application/json

{
  "query": "사무용 책상 2개와 의자 2개가 필요합니다",
  "temperature": 0.7,
  "max_tokens": 512
}
```

**응답:**
```json
{
  "success": true,
  "result": {
    "items": ["사무용 책상", "사무용 의자"],
    "quantities": ["2개", "2개"],
    "urgency": "보통",
    "budget_range": "미정"
  },
  "metrics": {
    "response_time": 1.234,
    "quality_score": 8.5
  }
}
```

### 3. RAG 검색

#### 벡터 검색 테스트
```http
POST /api/rag/test
Content-Type: application/json

{
  "query": "사무용 의자",
  "limit": 5
}
```

### 4. 워크플로우

#### 전체 워크플로우 실행
```http
POST /api/workflow/test
Content-Type: application/json

{
  "query": "사무용품 구매",
  "enable_data_collection": true,
  "enable_rag_search": true,
  "enable_document_generation": true,
  "max_items_per_platform": 10
}
```

### 5. 데이터 수집

#### G2B 검색
```http
POST /api/g2b/search
Content-Type: application/json

{
  "limit": 20,
  "start_date": "20250520",
  "end_date": "20250527"
}
```

#### 쿠팡 상품 검색
```http
POST /api/coupang/search?query=사무용책상&limit=20
```

#### 하이브리드 검색 (모든 플랫폼 통합)
```http
POST /api/search/hybrid
Content-Type: application/json

{
  "query": "사무용 책상",
  "filters": {
    "min_price": 200000,
    "max_price": 800000
  }
}
```

### 6. 문서 생성

#### 조달 보고서 생성
```http
POST /api/document/report
Content-Type: application/json

{
  "products": [...],
  "requirements": {
    "category": "사무용품",
    "budget_min": 300000,
    "budget_max": 600000
  }
}
```

#### 문서 타입 조회
```http
GET /api/documents/types
```

#### 문서 폼 필드 조회
```http
GET /api/documents/{document_type}/fields
```

#### 문서 생성
```http
POST /api/documents/generate
Content-Type: application/json

{
  "document_type": "procurement_request",
  "form_data": {
    "title": "사무용품 구매 요청",
    "items": ["책상", "의자"],
    "quantities": [2, 2]
  }
}
```

### 7. 성능 분석

#### 성능 데이터 조회
```http
GET /api/analytics/performance?days=7
```

#### 테스트 이력 조회
```http
GET /api/test/history?limit=50&test_type=llm_analysis
```

### 8. 통합 조달 워크플로우

#### 완전한 조달 프로세스 실행
```http
POST /api/procurement/complete
Content-Type: application/json

{
  "query": "사무용 책상 구매",
  "requirements": {
    "budget_min": 300000,
    "budget_max": 600000,
    "delivery_days": 14,
    "specifications": {
      "size": "1800x800mm 이상",
      "material": "목재"
    }
  }
}
```

---

## 🔧 내부 모듈 API

### 1. DocumentGenerator (문서 생성)

```python
from modules import DocumentGenerator

generator = DocumentGenerator()

# 제품 분석 보고서
report = await generator.generate_product_analysis_report(
    product=unified_product,
    requirement=procurement_requirement,
    matching_scores={"price": 0.8, "quality": 0.9}
)

# 비교 보고서
comparison = await generator.generate_comparison_report(
    products=[product1, product2],
    requirement=requirement,
    analysis_results=results
)
```

### 2. AdvancedRAGModule (고급 검색)

```python
from modules import AdvancedRAGModule

rag = AdvancedRAGModule()

# 하이브리드 검색
results = await rag.hybrid_search("사무용 책상", k=10)

# 요구사항 매칭
matches = await rag.match_products_to_requirements(products, requirements)
```

### 3. VectorDbModule (벡터 데이터베이스)

```python
from modules import VectorDbModule

vector_db = VectorDbModule()

# 상품 데이터 추가
vector_db.add_product_data(product_data)

# 유사 상품 검색
similar_products = vector_db.search_similar_products("사무용 의자", limit=5)

# 조달 이력 추가
vector_db.add_procurement_history(procurement_data)
```

### 4. LlmModule (LLM 연동)

```python
from modules import LlmModule

llm = LlmModule()

# 서버 상태 확인
if llm.check_server_health():
    # 조달 요청 분석
    analysis = llm.analyze_procurement_request("사무용 책상 2개 필요")
    
    # 추천 생성
    recommendation = llm.generate_procurement_recommendation(analysis)
```

---

## 🌟 사용 예시

### 1. 기본적인 상품 검색

```python
import asyncio
from modules.coupang_api_client import CoupangAuth, RateLimitedCoupangClient

async def search_products():
    auth = CoupangAuth("access_key", "secret_key", "vendor_id")
    
    async with RateLimitedCoupangClient(auth) as client:
        # 쿠팡에서 상품 검색
        coupang_results = await client.search_products("사무용 책상")
        print(f"쿠팡 검색 결과: {len(coupang_results['items'])}개")
        
        # G2B에서 입찰공고 검색
        from modules.g2b_api_client import G2BAPIClient
        async with G2BAPIClient() as g2b_client:
            g2b_results = await g2b_client.get_bid_announcements({
                'limit': 10
            })
            print(f"G2B 검색 결과: {len(g2b_results['items'])}개")

asyncio.run(search_products())
```

### 2. Web API 클라이언트 사용

```javascript
// JavaScript에서 API 호출
async function testLLM() {
    const response = await fetch('/api/llm/test', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            query: '사무용 책상 2개와 의자 4개가 필요합니다',
            temperature: 0.7,
            max_tokens: 512
        })
    });
    
    const result = await response.json();
    console.log('LLM 분석 결과:', result);
}
```

### 3. 완전한 조달 워크플로우

```python
async def complete_procurement_workflow():
    import aiohttp
    
    async with aiohttp.ClientSession() as session:
        # 통합 조달 워크플로우 실행
        async with session.post('http://localhost:8080/api/procurement/complete', 
                               json={
                                   'query': '사무용 책상 구매',
                                   'requirements': {
                                       'budget_min': 300000,
                                       'budget_max': 600000,
                                       'delivery_days': 14
                                   }
                               }) as response:
            result = await response.json()
            
            print("검색 결과:", len(result['search_results']))
            print("매칭 분석:", result['matching_analysis'])
            print("생성된 보고서:", result['generated_report'][:200])
```

---

## ⚠️ 에러 처리

### 일반적인 HTTP 상태 코드

- **200**: 성공
- **400**: 잘못된 요청 (필수 파라미터 누락 등)
- **404**: 리소스를 찾을 수 없음
- **500**: 서버 내부 오류

### 에러 응답 형식

```json
{
  "success": false,
  "error": "에러 메시지",
  "details": {
    "error_code": "INVALID_PARAM",
    "field": "query",
    "message": "검색어가 필요합니다"
  }
}
```

### 일반적인 에러 상황 및 해결 방법

#### 1. API 키 설정 오류
```bash
# 환경 변수가 설정되지 않은 경우
Error: API key not configured

# 해결: .env 파일에 올바른 API 키 설정
COUPANG_ACCESS_KEY=your_actual_key
```

#### 2. 서버 연결 오류
```bash
# LLM 서버에 연결할 수 없는 경우
Error: LLM server connection failed

# 해결: LLM 서버 상태 확인 및 URL 설정
LLM_SERVER_URL=http://localhost:11434
```

#### 3. Rate Limit 초과
```bash
# API 호출 한도 초과
Error: Rate limit exceeded

# 해결: 잠시 대기 후 재시도 (자동 처리됨)
```

### Fallback 메커니즘

시스템은 다음과 같은 fallback 메커니즘을 제공합니다:

1. **Mock 데이터**: API 키가 없을 때 테스트용 Mock 데이터 제공
2. **DummyModule**: 모듈 초기화 실패 시 안전한 더미 모듈 사용
3. **캐시**: 네트워크 오류 시 캐시된 데이터 사용
4. **우아한 성능 저하**: 일부 기능 실패 시에도 핵심 기능 유지

---

## ❓ FAQ

### Q1: API 키 없이 테스트할 수 있나요?
**A:** 네, 환경 변수가 설정되지 않으면 자동으로 Mock 데이터를 사용합니다. 개발 및 테스트 목적으로 충분합니다.

### Q2: 동시 요청 수에 제한이 있나요?
**A:** 쿠팡 API는 기본적으로 초당 10개 요청으로 제한됩니다. Rate Limiting이 자동으로 적용됩니다.

### Q3: 데이터는 어떻게 저장되나요?
**A:** 
- 벡터 데이터: ChromaDB (./chroma_db)
- 테스트 결과: 메모리 (서버 재시작 시 초기화)
- 캐시: 메모리 (TTL 적용)

### Q4: 커스텀 문서 템플릿을 추가할 수 있나요?
**A:** 네, `DocumentFormGenerator`를 확장하여 새로운 문서 타입과 템플릿을 추가할 수 있습니다.

### Q5: 다른 쇼핑몰 API를 추가하려면?
**A:** `coupang_api_client.py`와 유사한 구조로 새로운 클라이언트를 만들고, `handlers.py`에서 통합하면 됩니다.

### Q6: 성능 최적화 방법은?
**A:** 
- 적절한 캐시 TTL 설정
- 불필요한 필드 제외
- 배치 처리 활용
- 비동기 처리 최대 활용

---

## 📞 지원 및 문의

- **개발팀 연락처**: [개발팀 이메일]
- **이슈 리포트**: [GitHub Issues 링크]
- **API 업데이트**: [업데이트 공지 채널]

---

**🔄 문서 업데이트**
이 문서는 API 변경 사항에 따라 지속적으로 업데이트됩니다. 최신 버전은 항상 프로젝트 레포지토리에서 확인하세요.
