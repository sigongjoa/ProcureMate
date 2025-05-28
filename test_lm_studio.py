#!/usr/bin/env python3
"""LM Studio 직접 테스트"""

import requests
import json

def test_lm_studio_connection():
    """LM Studio 연결 테스트"""
    
    server_url = "http://localhost:1234"
    
    print("=== LM Studio 연결 테스트 ===")
    
    # 1. 서버 상태 확인
    print("1. 서버 상태 확인...")
    try:
        response = requests.get(f"{server_url}/v1/models", timeout=5)
        print(f"   상태 코드: {response.status_code}")
        print(f"   헤더: {dict(response.headers)}")
        print(f"   응답 길이: {len(response.text)}")
        print(f"   응답 내용 (처음 200자): {response.text[:200]}")
        
        if response.status_code == 200:
            models = response.json()
            print(f"   모델 수: {len(models.get('data', []))}")
            if models.get('data'):
                for model in models['data']:
                    print(f"   - {model.get('id', 'Unknown')}")
            else:
                print("   ⚠️ 로드된 모델이 없습니다!")
        else:
            print(f"   ❌ 오류 응답: {response.text}")
    except Exception as e:
        print(f"   ❌ 연결 실패: {e}")
        return False
    
    # 2. 직접 채팅 API 테스트
    print("\n2. 채팅 API 테스트...")
    try:
        payload = {
            "model": "llambricks-horizon-ai-korean-llama-3.1-1ft-dpo-8b",
            "messages": [{"role": "user", "content": "안녕하세요"}],
            "max_tokens": 50,
            "temperature": 0.7
        }
        
        print(f"   요청 페이로드: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        
        response = requests.post(
            f"{server_url}/v1/chat/completions",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"   상태 코드: {response.status_code}")
        print(f"   응답 헤더: {dict(response.headers)}")
        print(f"   응답 내용: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            completion = result["choices"][0]["message"]["content"]
            print(f"   ✅ 성공! 응답: {completion}")
            return True
        else:
            print(f"   ❌ 오류: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ 채팅 API 오류: {e}")
        return False

def test_llm_module():
    """LLM 모듈 직접 테스트"""
    print("\n=== LLM 모듈 테스트 ===")
    
    import sys
    from pathlib import Path
    
    # 프로젝트 루트 추가
    project_root = str(Path(__file__).parent)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    try:
        from modules.llm_module import LlmModule
        
        llm = LlmModule()
        print("1. LLM 모듈 생성 완료")
        
        # 서버 상태 확인
        server_ok = llm.check_server_health()
        print(f"2. 서버 상태: {'정상' if server_ok else '비정상'}")
        
        if server_ok:
            # 실제 요청 테스트
            test_request = "사무용 의자 5개 필요합니다"
            print(f"3. 테스트 요청: {test_request}")
            
            analysis = llm.analyze_procurement_request(test_request)
            print(f"4. 분석 결과: {json.dumps(analysis, indent=2, ensure_ascii=False)}")
            
            return True
        else:
            print("   ❌ 서버 상태 비정상으로 인한 테스트 중단")
            return False
            
    except Exception as e:
        print(f"   ❌ LLM 모듈 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("LM Studio 연결 및 LLM 모듈 테스트를 시작합니다.\n")
    
    # 1. 직접 연결 테스트
    direct_ok = test_lm_studio_connection()
    
    # 2. 모듈 테스트
    module_ok = test_llm_module()
    
    print("\n=== 테스트 결과 요약 ===")
    print(f"직접 연결: {'✅ 성공' if direct_ok else '❌ 실패'}")
    print(f"모듈 테스트: {'✅ 성공' if module_ok else '❌ 실패'}")
    
    if not direct_ok:
        print("\n🔧 해결 방법:")
        print("1. LM Studio가 실행 중인지 확인")
        print("2. LM Studio에서 모델을 로드했는지 확인")
        print("3. LM Studio의 로컬 서버가 localhost:1234에서 실행 중인지 확인")
        print("4. LM Studio 설정에서 CORS가 활성화되어 있는지 확인")
