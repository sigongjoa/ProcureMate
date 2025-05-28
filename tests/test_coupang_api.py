#!/usr/bin/env python3

import pytest
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from modules.coupang_api_client import CoupangAuth, RateLimitedCoupangClient, CoupangAPIClient

class TestCoupangAPI:
    
    @pytest.fixture
    def auth(self):
        return CoupangAuth("test_access", "test_secret", "test_vendor")
    
    @pytest.fixture
    def client(self, auth):
        return CoupangAPIClient(auth)
    
    @pytest.fixture
    def rate_limited_client(self, auth):
        return RateLimitedCoupangClient(auth, rate_limit=2)
    
    def test_hmac_signature_generation(self, auth):
        try:
            headers = auth.generate_hmac_signature("GET", "/test", "param=value")
            assert "Authorization" in headers
            assert "CEA algorithm=HmacSHA256" in headers["Authorization"]
            assert "X-Requested-By" in headers
            print("DEBUG: HMAC 서명 생성 성공")
        except Exception as e:
            print(f"ERROR: {str(e)}")
            raise
    
    @pytest.mark.asyncio
    async def test_search_products(self, client):
        try:
            result = await client.search_products("테스트 상품", limit=5)
            assert isinstance(result, list)
            print(f"DEBUG: 상품 검색 결과: {len(result)}건")
        except Exception as e:
            print(f"ERROR: {str(e)}")
            raise
    
    @pytest.mark.asyncio
    async def test_get_product_details(self, client):
        try:
            result = await client.get_product_details("test-product-123")
            assert isinstance(result, dict)
            print("DEBUG: 상품 상세정보 조회 테스트 통과")
        except Exception as e:
            print(f"ERROR: {str(e)}")
            raise
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self, rate_limited_client):
        try:
            import time
            start_time = time.time()
            
            # 연속 3회 요청
            tasks = [
                rate_limited_client.make_request("GET", "/test1"),
                rate_limited_client.make_request("GET", "/test2"), 
                rate_limited_client.make_request("GET", "/test3")
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            elapsed = time.time() - start_time
            
            # Rate limiting으로 인해 최소 1초는 걸려야 함
            assert elapsed >= 1.0
            print(f"DEBUG: Rate limiting 테스트 통과 (소요시간: {elapsed:.2f}초)")
        except Exception as e:
            print(f"ERROR: {str(e)}")
            raise

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
