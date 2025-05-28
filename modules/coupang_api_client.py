#!/usr/bin/env python3
"""
쿠팡 API 클라이언트
쿠팡 상품 정보 수집 및 처리
"""

import aiohttp
import asyncio
import os
import hmac
import hashlib
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import deque
from asyncio import Semaphore
from utils import get_logger

logger = get_logger(__name__)

class CoupangAuth:
    """쿠팡 HMAC 인증 처리"""
    
    def __init__(self, access_key: str, secret_key: str, vendor_id: str):
        self.access_key = access_key
        self.secret_key = secret_key
        self.vendor_id = vendor_id
    
    def generate_hmac_signature(self, method: str, path: str, query: str = "") -> Dict[str, str]:
        """HMAC 서명 생성"""
        timestamp = datetime.utcnow().strftime('%y%m%dT%H%M%SZ')
        message = f"{timestamp}{method}{path}{query}"
        
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return {
            'Authorization': f'CEA algorithm=HmacSHA256, access-key={self.access_key}, signed-date={timestamp}, signature={signature}',
            'X-Requested-By': self.vendor_id,
            'Content-Type': 'application/json'
        }

class RateLimitedCoupangClient:
    """Rate Limiting이 적용된 쿠팡 API 클라이언트"""
    
    def __init__(self, auth: CoupangAuth, rate_limit: int = 10):
        self.auth = auth
        self.base_url = "https://api-gateway.coupang.com"
        self.rate_limit = rate_limit
        self.semaphore = Semaphore(rate_limit)
        self.request_times = deque(maxlen=rate_limit)
        self.session = None
        self._cache = {}
        self._cache_ttl = timedelta(minutes=30)
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def _wait_if_needed(self):
        """Rate limit를 준수하기 위한 대기 로직"""
        if len(self.request_times) == self.rate_limit:
            oldest_request_time = self.request_times[0]
            elapsed = time.time() - oldest_request_time
            if elapsed < 1.0:
                await asyncio.sleep(1.0 - elapsed)
    
    async def _make_request(self, method: str, endpoint: str, params: Dict = None, data: Dict = None) -> Dict:
        """Rate limit이 적용된 API 요청"""
        async with self.semaphore:
            await self._wait_if_needed()
            self.request_times.append(time.time())
            
            cache_key = f"coupang_{endpoint}_{hash(str(params))}"
            cached_data = self._get_cached_data(cache_key)
            if cached_data:
                logger.info("캐시된 쿠팡 데이터 반환")
                return cached_data
            
            headers = self.auth.generate_hmac_signature(method, endpoint)
            url = f"{self.base_url}{endpoint}"
            
            if method.upper() == 'GET':
                async with self.session.get(url, headers=headers, params=params) as response:
                    result = await self._handle_response(response)
                    self._set_cache(cache_key, result)
                    return result
            else:
                async with self.session.request(method, url, headers=headers, json=data, params=params) as response:
                    result = await self._handle_response(response)
                    self._set_cache(cache_key, result)
                    return result
    
    async def _handle_response(self, response: aiohttp.ClientResponse) -> Dict:
        """API 응답 처리"""
        if response.status == 200:
            return await response.json()
        elif response.status == 401:
            raise Exception("쿠팡 API 인증 실패 - ACCESS_KEY, SECRET_KEY, VENDOR_ID 확인 필요")
        elif response.status == 403:
            raise Exception("쿠팡 API 접근 권한 없음 - 파트너 등록 및 승인 필요")
        elif response.status == 429:
            logger.error("쿠팡 API Rate Limit 초과")
            await asyncio.sleep(1)
            raise Exception("쿠팡 API Rate Limit 초과")
        else:
            response_text = await response.text()
            logger.error(f"쿠팡 API 오류: {response.status} - {response_text}")
            raise Exception(f"쿠팡 API 오류: {response.status}")
    
    async def search_products(self, query: str, params: Dict = None) -> Dict:
        """상품 검색"""
        logger.info(f"쿠팡 상품 검색: {query}")
        
        search_params = {
            'keyword': query,
            'limit': params.get('limit', 50) if params else 50,
            'page': params.get('page', 1) if params else 1
        }
        
        if params:
            if params.get('min_price'):
                search_params['minPrice'] = params['min_price']
            if params.get('max_price'):
                search_params['maxPrice'] = params['max_price']
            if params.get('category'):
                search_params['categoryId'] = params['category']
        
        endpoint = "/v2/providers/affiliate_open_api/apis/openapi/products/search"
        raw_data = await self._make_request('GET', endpoint, search_params)
        
        return self._process_product_search_data(raw_data, query)
    
    async def get_product_details(self, product_id: str) -> Dict:
        """상품 상세 정보 조회"""
        logger.info(f"쿠팡 상품 상세 조회: {product_id}")
        
        endpoint = f"/v2/providers/affiliate_open_api/apis/openapi/products/{product_id}"
        raw_data = await self._make_request('GET', endpoint)
        
        return self._process_product_detail_data(raw_data)
    
    async def get_product_categories(self) -> Dict:
        """상품 카테고리 조회"""
        logger.info("쿠팡 카테고리 조회")
        
        endpoint = "/v2/providers/affiliate_open_api/apis/openapi/categories"
        raw_data = await self._make_request('GET', endpoint)
        
        return self._process_category_data(raw_data)
    
    def _process_product_search_data(self, raw_data: Dict, query: str) -> Dict:
        """상품 검색 데이터 처리"""
        products = raw_data.get('data', {}).get('productData', [])
        
        processed_items = []
        for product in products:
            processed_item = {
                'id': f"coupang_{product.get('productId', 'unknown')}",
                'product_id': product.get('productId'),
                'name': product.get('productName', ''),
                'price': product.get('productPrice', 0),
                'original_price': product.get('productOriginalPrice', 0),
                'discount_rate': product.get('discountRate', 0),
                'image_url': product.get('productImage', ''),
                'url': product.get('productUrl', ''),
                'category_name': product.get('categoryName', ''),
                'vendor_name': product.get('vendorName', ''),
                'rating': product.get('rating', 0),
                'review_count': product.get('reviewCount', 0),
                'delivery_fee': product.get('deliveryFee', 0),
                'is_available': product.get('isFreeShipping', False),
                'source': 'coupang',
                'search_query': query,
                'raw_data': product
            }
            processed_items.append(processed_item)
        
        return {
            'success': True,
            'total_count': len(processed_items),
            'items': processed_items,
            'source': 'coupang',
            'query': query
        }

    def _process_product_detail_data(self, raw_data: Dict) -> Dict:
        """상품 상세 데이터 처리"""
        product = raw_data.get('data', {})
        
        processed_item = {
            'id': f"coupang_{product.get('productId', 'unknown')}",
            'product_id': product.get('productId'),
            'name': product.get('productName', ''),
            'description': product.get('productDescription', ''),
            'price': product.get('productPrice', 0),
            'original_price': product.get('productOriginalPrice', 0),
            'discount_rate': product.get('discountRate', 0),
            'images': product.get('productImages', []),
            'category_path': product.get('categoryPath', []),
            'specifications': product.get('productSpecs', {}),
            'vendor_info': product.get('vendorInfo', {}),
            'delivery_info': product.get('deliveryInfo', {}),
            'rating': product.get('rating', 0),
            'review_count': product.get('reviewCount', 0),
            'source': 'coupang',
            'raw_data': product
        }
        
        return {
            'success': True,
            'item': processed_item,
            'source': 'coupang'
        }

    def _process_category_data(self, raw_data: Dict) -> Dict:
        """카테고리 데이터 처리"""
        categories = raw_data.get('data', [])
        
        processed_categories = []
        for category in categories:
            processed_category = {
                'id': category.get('categoryId'),
                'name': category.get('categoryName', ''),
                'parent_id': category.get('parentCategoryId'),
                'level': category.get('level', 0),
                'children': category.get('children', []),
                'source': 'coupang'
            }
            processed_categories.append(processed_category)
        
        return {
            'success': True,
            'categories': processed_categories,
            'source': 'coupang'
        }
    
    def _get_cached_data(self, cache_key: str) -> Optional[Dict]:
        """캐시된 데이터 조회"""
        if cache_key in self._cache:
            cached_data, timestamp = self._cache[cache_key]
            if datetime.now() - timestamp < self._cache_ttl:
                return cached_data
        return None
    
    def _set_cache(self, cache_key: str, data: Dict):
        """데이터 캐시 저장"""
        self._cache[cache_key] = (data, datetime.now())

async def test_coupang_client():
    """쿠팡 클라이언트 테스트"""
    access_key = os.getenv("COUPANG_ACCESS_KEY")
    secret_key = os.getenv("COUPANG_SECRET_KEY") 
    vendor_id = os.getenv("COUPANG_VENDOR_ID")
    
    if not access_key or not secret_key or not vendor_id:
        raise Exception("쿠팡 API 설정 필요: COUPANG_ACCESS_KEY, COUPANG_SECRET_KEY, COUPANG_VENDOR_ID 환경변수 설정")
    
    auth = CoupangAuth(access_key, secret_key, vendor_id)
    
    async with RateLimitedCoupangClient(auth) as client:
        search_result = await client.search_products("사무용 책상", {
            'limit': 10,
            'min_price': 100000,
            'max_price': 1000000
        })
        print(f"상품 검색 결과: {len(search_result.get('items', []))}건")
        
        category_result = await client.get_product_categories()
        print(f"카테고리 조회 결과: {len(category_result.get('categories', []))}개")
        
        if search_result.get('items'):
            first_product = search_result['items'][0]
            detail_result = await client.get_product_details(first_product['product_id'])
            print(f"상품 상세 조회 성공: {detail_result.get('success', False)}")

if __name__ == "__main__":
    asyncio.run(test_coupang_client())
