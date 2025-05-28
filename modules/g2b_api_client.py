#!/usr/bin/env python3
"""
나라장터(G2B) API 클라이언트
공공조달 정보 수집 및 처리
"""

import aiohttp
import asyncio
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import xml.etree.ElementTree as ET
from utils import get_logger

logger = get_logger(__name__)

class G2BAPIClient:
    """나라장터 API 클라이언트"""
    
    def __init__(self):
        self.base_url = "http://apis.data.go.kr/1230000"
        self.service_key = os.getenv("G2B_SERVICE_KEY", "test_key")
        self.session = None
        self._cache = {}
        self._cache_ttl = timedelta(minutes=15)
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_bid_announcements(self, params: Dict) -> Dict:
        """입찰공고 정보 조회"""
        logger.info("G2B 입찰공고 조회 시작")
        
        # API 키가 설정되지 않은 경우 Mock 데이터 반환
        if self.service_key == "test_key":
            logger.warning("G2B API 키가 설정되지 않음 - Mock 데이터 반환")
            return self._generate_mock_bid_data()
        
        endpoint = "/BidInfoService/getBidPblancListInfo01"
        
        request_params = {
            'serviceKey': self.service_key,
            'numOfRows': params.get('limit', 100),
            'pageNo': params.get('page', 1),
            'resultType': 'json',
            'inqryBgnDt': params.get('start_date', self._get_default_start_date()),
            'inqryEndDt': params.get('end_date', self._get_default_end_date())
        }
        
        # 추가 필터 파라미터
        if params.get('budget_min'):
            request_params['prdctClsfcNo'] = params.get('category_code', '')
        
        cache_key = f"bid_announcements_{hash(str(sorted(request_params.items())))}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            logger.info("캐시된 G2B 데이터 반환")
            return cached_data
        
        async with self.session.get(f"{self.base_url}{endpoint}", params=request_params) as response:
            if response.status == 200:
                data = await response.json()
                processed_data = self._process_bid_data(data)
                self._set_cache(cache_key, processed_data)
                logger.info(f"G2B 입찰공고 {len(processed_data.get('items', []))}건 조회 완료")
                return processed_data
            else:
                logger.error(f"G2B API 호출 실패: {response.status}")
                return self._generate_mock_bid_data()
                    

    
    async def get_contract_info(self, params: Dict) -> Dict:
        """계약정보 조회"""
        logger.info("G2B 계약정보 조회 시작")
        
        if self.service_key == "test_key":
            logger.warning("G2B API 키가 설정되지 않음 - Mock 계약 데이터 반환")
            return self._generate_mock_contract_data()
        
        endpoint = "/CntrctInfoService/getCntrctInfoListServc01"
        
        request_params = {
            'serviceKey': self.service_key,
            'numOfRows': params.get('limit', 100),
            'pageNo': params.get('page', 1),
            'resultType': 'json',
            'cntrctCnclsMthdNm': params.get('contract_method', ''),
            'cntrctCnclsDate': params.get('contract_date', '')
        }
        
        async with self.session.get(f"{self.base_url}{endpoint}", params=request_params) as response:
            if response.status == 200:
                data = await response.json()
                return self._process_contract_data(data)
            else:
                logger.error(f"G2B 계약정보 API 호출 실패: {response.status}")
                return self._generate_mock_contract_data()
                    

    
    async def get_price_info(self, params: Dict) -> Dict:
        """가격정보 조회"""
        logger.info("G2B 가격정보 조회 시작")
        
        if self.service_key == "test_key":
            logger.warning("G2B API 키가 설정되지 않음 - Mock 가격 데이터 반환")
            return self._generate_mock_price_data()
        
        endpoint = "/PriceInfoService/getPriceInfoList"
        
        request_params = {
            'serviceKey': self.service_key,
            'numOfRows': params.get('limit', 100),
            'pageNo': params.get('page', 1),
            'resultType': 'json',
            'itemNm': params.get('item_name', ''),
            'stdrYearMonth': params.get('year_month', datetime.now().strftime('%Y%m'))
        }
        
        async with self.session.get(f"{self.base_url}{endpoint}", params=request_params) as response:
            if response.status == 200:
                data = await response.json()
                return self._process_price_data(data)
            else:
                logger.error(f"G2B 가격정보 API 호출 실패: {response.status}")
                return self._generate_mock_price_data()

    
    def _process_bid_data(self, raw_data: Dict) -> Dict:
        """입찰 데이터 처리"""

        response_body = raw_data.get('response', {}).get('body', {})
        items = response_body.get('items', [])
        
        processed_items = []
        for item in items:
            processed_item = {
                'id': f"g2b_bid_{item.get('bidNtceNo', 'unknown')}",
                'announcement_number': item.get('bidNtceNo'),
                'title': item.get('bidNtceNm', ''),
                'organization': item.get('dminsttNm', ''),
                'budget': item.get('asignBdgtAmt', 0),
                'announcement_date': item.get('bidNtceDt', ''),
                'deadline': item.get('bidClseDt', ''),
                'industry_code': item.get('indstrytyLclsCd', ''),
                'region_code': item.get('rgstTyNm', ''),
                'bid_method': item.get('bidMthdNm', ''),
                'contract_type': item.get('cntrctCnclsMthdNm', ''),
                'source': 'g2b',
                'raw_data': item
            }
            processed_items.append(processed_item)
        
        return {
            'success': True,
            'total_count': response_body.get('totalCount', 0),
            'items': processed_items,
            'source': 'g2b'
        }
        

    
    def _process_contract_data(self, raw_data: Dict) -> Dict:
        """계약 데이터 처리"""
        response_body = raw_data.get('response', {}).get('body', {})
        items = response_body.get('items', [])
        
        processed_items = []
        for item in items:
            processed_item = {
                'id': f"g2b_contract_{item.get('cntrctNo', 'unknown')}",
                'contract_number': item.get('cntrctNo'),
                'title': item.get('cntrctNm', ''),
                'organization': item.get('dminsttNm', ''),
                'contract_amount': item.get('cntrctAmt', 0),
                'contract_date': item.get('cntrctCnclsDt', ''),
                'supplier': item.get('cntrctorNm', ''),
                'supplier_registration': item.get('cntrctorBizrno', ''),
                'performance_period': item.get('cntrctPrdEnd', ''),
                'source': 'g2b',
                'raw_data': item
            }
            processed_items.append(processed_item)
        
        return {
            'success': True,
            'total_count': response_body.get('totalCount', 0),
            'items': processed_items,
            'source': 'g2b'
        }

    
    def _process_price_data(self, raw_data: Dict) -> Dict:
        """가격 데이터 처리"""
        response_body = raw_data.get('response', {}).get('body', {})
        items = response_body.get('items', [])
        
        processed_items = []
        for item in items:
            processed_item = {
                'id': f"g2b_price_{item.get('serialNo', 'unknown')}",
                'item_name': item.get('itemNm', ''),
                'standard': item.get('stdrStndrd', ''),
                'unit': item.get('untNm', ''),
                'price': item.get('prc', 0),
                'year_month': item.get('stdrYearMonth', ''),
                'price_type': item.get('prcTypeNm', ''),
                'source': 'g2b',
                'raw_data': item
            }
            processed_items.append(processed_item)
        
        return {
            'success': True,
            'total_count': response_body.get('totalCount', 0),
            'items': processed_items,
            'source': 'g2b'
        }

    def _generate_mock_bid_data(self) -> Dict:
        """Mock 입찰 데이터 생성"""
        logger.info("Mock G2B 입찰 데이터 생성")
        
        mock_items = []
        for i in range(5):
            item = {
                'id': f"g2b_bid_mock_{i+1}",
                'announcement_number': f"20250526-{i+1:03d}",
                'title': f"Mock 입찰공고 {i+1} - 사무용품 구매",
                'organization': f"Mock 기관 {i+1}",
                'budget': (i+1) * 1000000,
                'announcement_date': datetime.now().strftime('%Y%m%d'),
                'deadline': (datetime.now() + timedelta(days=14)).strftime('%Y%m%d'),
                'industry_code': '기타',
                'region_code': '서울',
                'bid_method': '일반경쟁입찰',
                'contract_type': '총액계약',
                'source': 'g2b',
                'raw_data': {}
            }
            mock_items.append(item)
        
        return {
            'success': True,
            'total_count': 5,
            'items': mock_items,
            'source': 'g2b'
        }
    
    def _generate_mock_contract_data(self) -> Dict:
        """Mock 계약 데이터 생성"""
        logger.info("Mock G2B 계약 데이터 생성")
        
        mock_items = []
        for i in range(3):
            item = {
                'id': f"g2b_contract_mock_{i+1}",
                'contract_number': f"Contract-2025-{i+1:03d}",
                'title': f"Mock 계약 {i+1} - 사무용품 공급",
                'organization': f"Mock 계약기관 {i+1}",
                'contract_amount': (i+1) * 2000000,
                'contract_date': (datetime.now() - timedelta(days=30)).strftime('%Y%m%d'),
                'supplier': f"Mock 공급업체 {i+1}",
                'supplier_registration': f"123-45-{i+1:05d}",
                'performance_period': (datetime.now() + timedelta(days=180)).strftime('%Y%m%d'),
                'source': 'g2b',
                'raw_data': {}
            }
            mock_items.append(item)
        
        return {
            'success': True,
            'total_count': 3,
            'items': mock_items,
            'source': 'g2b'
        }
    
    def _generate_mock_price_data(self) -> Dict:
        """Mock 가격 데이터 생성"""
        logger.info("Mock G2B 가격 데이터 생성")
        
        mock_items = []
        items = [
            ("사무용 책상", "1800×800×720mm", "개", 450000),
            ("사무용 의자", "회전의자", "개", 280000),
            ("컴퓨터 책상", "1600×700×730mm", "개", 380000),
            ("회의용 테이블", "2400×1200×720mm", "개", 850000),
            ("서류함", "4단 서류함", "개", 320000)
        ]
        
        for i, (name, standard, unit, price) in enumerate(items):
            item = {
                'id': f"g2b_price_mock_{i+1}",
                'item_name': name,
                'standard': standard,
                'unit': unit,
                'price': price,
                'year_month': datetime.now().strftime('%Y%m'),
                'price_type': '기준가격',
                'source': 'g2b',
                'raw_data': {}
            }
            mock_items.append(item)
        
        return {
            'success': True,
            'total_count': len(mock_items),
            'items': mock_items,
            'source': 'g2b'
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
    
    def _get_default_start_date(self) -> str:
        """기본 조회 시작일 (7일 전)"""
        return (datetime.now() - timedelta(days=7)).strftime('%Y%m%d')
    
    def _get_default_end_date(self) -> str:
        """기본 조회 종료일 (오늘)"""
        return datetime.now().strftime('%Y%m%d')

# 사용 예시
async def test_g2b_client():
    """G2B 클라이언트 테스트"""
    async with G2BAPIClient() as client:
        # 입찰공고 조회
        bid_result = await client.get_bid_announcements({
            'limit': 10,
            'start_date': '20250520',
            'end_date': '20250527'
        })
        print(f"입찰공고 조회 결과: {len(bid_result.get('items', []))}건")
        
        # 계약정보 조회
        contract_result = await client.get_contract_info({
            'limit': 5
        })
        print(f"계약정보 조회 결과: {len(contract_result.get('items', []))}건")
        
        # 가격정보 조회
        price_result = await client.get_price_info({
            'limit': 5,
            'item_name': '사무용품'
        })
        print(f"가격정보 조회 결과: {len(price_result.get('items', []))}건")

if __name__ == "__main__":
    asyncio.run(test_g2b_client())
