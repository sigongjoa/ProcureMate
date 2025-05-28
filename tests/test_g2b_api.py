#!/usr/bin/env python3

import pytest
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from modules.g2b_api_client import G2BAPIClient

class TestG2BAPIClient:
    
    @pytest.fixture
    def client(self):
        return G2BAPIClient()
    
    def test_client_initialization(self, client):
        assert client.base_url == "http://apis.data.go.kr/1230000"
        assert client.service_key is not None
        print("DEBUG: G2B 클라이언트 초기화 성공")
    
    @pytest.mark.asyncio
    async def test_get_bid_announcements(self, client):
        try:
            async with client:
                params = {
                    'query': '사무용품',
                    'limit': 5
                }
                result = await client.get_bid_announcements(params)
                assert isinstance(result, dict)
                print(f"DEBUG: 입찰공고 검색 결과: {len(result.get('items', []))}건")
        except Exception as e:
            print(f"ERROR: {str(e)}")
            raise
    
    @pytest.mark.asyncio  
    async def test_get_contract_info(self, client):
        try:
            async with client:
                result = await client.get_contract_info({'contractId': 'test-123'})
                assert isinstance(result, dict)
                print("DEBUG: 계약정보 조회 테스트 통과")
        except Exception as e:
            print(f"ERROR: {str(e)}")
            raise
    
    @pytest.mark.asyncio
    async def test_cache_functionality(self, client):
        try:
            async with client:
                params = {'query': 'test', 'limit': 1}
                
                # 첫 번째 호출
                result1 = await client.get_cached_data(
                    'test_key', 
                    client.get_bid_announcements,
                    params
                )
                
                # 두 번째 호출 (캐시에서)
                result2 = await client.get_cached_data(
                    'test_key',
                    client.get_bid_announcements, 
                    params
                )
                
                assert result1 == result2
                print("DEBUG: 캐시 기능 정상 작동")
        except Exception as e:
            print(f"ERROR: {str(e)}")
            raise

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
