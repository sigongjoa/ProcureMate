# LM Studio 설정 가이드

## 문제 상황
현재 LM Studio에 **임베딩 모델만** 로드되어 있어서 채팅 완료 API를 사용할 수 없습니다.

## 해결 방법

### 1. 채팅용 모델 다운로드
LM Studio에서 다음 중 하나의 모델을 다운로드:

**추천 모델 (한국어 지원):**
- `microsoft/Phi-3-mini-4k-instruct` (3.8GB)
- `Qwen/Qwen2.5-7B-Instruct` (4.4GB) 
- `meta-llama/Llama-3.2-3B-Instruct` (2GB)

### 2. 모델 로드
1. LM Studio 실행
2. 왼쪽 메뉴에서 "Chat" 클릭
3. 다운로드한 모델 선택하여 로드
4. "Load model" 버튼 클릭

### 3. 서버 시작
1. "Developer" 탭 클릭
2. "Start Server" 버튼 클릭
3. 포트 1234에서 서버 실행 확인

### 4. 확인 방법
브라우저에서 다음 URL 접속:
```
http://localhost:1234/v1/models
```

다음과 같이 채팅 모델이 표시되어야 함:
```json
{
  "data": [
    {
      "id": "microsoft/Phi-3-mini-4k-instruct",
      "object": "model",
      "owned_by": "organization_owner"
    }
  ]
}
```

## 현재 상태
- ✅ LM Studio 서버 실행 중 (포트 1234)
- ❌ 채팅용 모델 없음 (임베딩 모델만 로드됨)
  - `text-embedding-nomic-embed-text-v1.5`
  - `text-embedding-nomic-embed-text-v1.5:2`

## 추가 도움
- LM Studio 공식 문서: https://lmstudio.ai/docs
- 모델 검색: https://huggingface.co/models
