#!/usr/bin/env python3
"""
업데이트된 DataCollectorModule - 고급 API 클라이언트 통합
"""

import asyncio
import requests
import time
from typing import Dict, List, Any, Optional
from urllib.parse import urlencode
import hashlib
import hmac
import base64
from datetime import datetime
from utils import get_logger, ModuleValidator
from config import ProcureMateSettings
from modules.g2b_api_client import G2BAPIClient
from modules.coupang_api_client import CoupangAuth, RateLimitedCoupangClient
from modules.data_processor import DataIntegrator, ProductDeduplicator, UnifiedProduct

logger = get_logger(__name__)

class DataCollectorModule:
    """고급 전자상거래 데이터 수집 모듈"""
    
    def __init__(self):
        # 기존 설정 유지 (하위 호환성)
        self.coupang_access_key = ProcureMateSettings.COUPANG_ACCESS_KEY
        self.coupang_secret_key = ProcureMateSettings.COUPANG_SECRET_KEY
        self.g2b_api_key = ProcureMateSettings.G2B_API_KEY
        self.validator = ModuleValidator("DataCollectorModule")
        
        # 새로운 API 클라이언트 초기화
        self.g2b_client = None
        self.coupang_client = None
        self.data_integrator = DataIntegrator()
        self.deduplicator = ProductDeduplicator()
        
        logger.info("업데이트된 DataCollectorModule 초기화")
    
    async def initialize_clients(self):
        """API 클라이언트 초기화"""

        # G2B 클라이언트 초기화
        self.g2b_client = G2BAPIClient()
        
        # 쿠팡 클라이언트 초기화
        coupang_auth = CoupangAuth(
            access_key=self.coupang_access_key or "test_key",
            secret_key=self.coupang_secret_key or "test_secret",
            vendor_id=ProcureMateSettings.COUPANG_VENDOR_ID or "test_vendor"
        )
        self.coupang_client = RateLimitedCoupangClient(coupang_auth)
        
        logger.info("API 클라이언트 초기화 완료")

    
    # === 기존 인터페이스 유지 (하위 호환성) ===
    
    def search_coupang_products(self, keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
        """쿠팡 상품 검색 (기존 인터페이스)"""

        # 비동기 함수를 동기적으로 호출
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results = loop.run_until_complete(self._async_search_coupang(keyword, limit))
        loop.close()
        
        return self._convert_unified_to_legacy_coupang(results)

    
    def search_g2b_products(self, keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
        """나라장터 상품 검색 (기존 인터페이스)"""

        # 비동기 함수를 동기적으로 호출
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results = loop.run_until_complete(self._async_search_g2b(keyword, limit))
        loop.close()
        
        return self._convert_unified_to_legacy_g2b(results)

    def search_all_platforms(self, keyword: str, limit_per_platform: int = 5) -> Dict[str, List[Dict[str, Any]]]:
        """모든 플랫폼에서 검색 (기존 인터페이스)"""
        logger.info(f"전체 플랫폼 검색 시작: {keyword}")
    
        # 비동기 함수를 동기적으로 호출
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results = loop.run_until_complete(self._async_search_all_platforms(keyword, limit_per_platform))
        loop.close()
        
        return results
        

    
    # === 새로운 고급 API 인터페이스 ===
    
    async def advanced_search_products(
        self, 
        keyword: str, 
        filters: Dict[str, Any] = None,
        enable_deduplication: bool = True
    ) -> Dict[str, Any]:
        """고급 상품 검색"""
        logger.info(f"고급 상품 검색 시작: {keyword}")
        
        if not self.g2b_client or not self.coupang_client:
            await self.initialize_clients()
        

        # 병렬 검색 실행
        g2b_task = self._async_search_g2b_advanced(keyword, filters)
        coupang_task = self._async_search_coupang_advanced(keyword, filters)
        
        g2b_data, coupang_data = await asyncio.gather(g2b_task, coupang_task)
        
        # 데이터 통합
        g2b_products = await self.data_integrator.integrate_g2b_data(g2b_data)
        coupang_products = await self.data_integrator.integrate_coupang_data(coupang_data)
        
        all_products = g2b_products + coupang_products
        
        # 중복 제거
        if enable_deduplication and all_products:
            duplicate_groups = await self.deduplicator.find_duplicates(all_products)
            all_products = self._remove_duplicates(all_products, duplicate_groups)
        
        # 결과 정리
        result = {
            'success': True,
            'total_count': len(all_products),
            'products': all_products,
            'source_counts': {
                'g2b': len(g2b_products),
                'coupang': len(coupang_products)
            },
            'deduplication_applied': enable_deduplication,
            'search_query': keyword,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"고급 검색 완료: 총 {len(all_products)}개 상품")
        return result
            

    async def search_by_category(
        self, 
        category: str, 
        budget_range: Dict[str, float] = None,
        limit: int = 20
    ) -> Dict[str, Any]:
        """카테고리별 상품 검색"""
        logger.info(f"카테고리별 검색: {category}")
        
        filters = {
            'category': category,
            'limit': limit
        }
        
        if budget_range:
            filters.update(budget_range)
        
        return await self.advanced_search_products(category, filters)
    
    async def search_procurement_cases(
        self, 
        organization: str = None,
        date_range: Dict[str, str] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """조달 사례 검색 (G2B 전용)"""
        logger.info(f"조달 사례 검색: 기관={organization}")
        
        if not self.g2b_client:
            await self.initialize_clients()
        

        # G2B 입찰공고 및 계약정보 검색
        params = {'limit': limit}
        
        if date_range:
            params.update(date_range)
        
        async with self.g2b_client as client:
            bid_data = await client.get_bid_announcements(params)
            contract_data = await client.get_contract_info(params)
        
        # 데이터 통합 및 분석
        all_cases = []
        
        # 입찰공고 데이터 처리
        if bid_data.get('success'):
            bid_products = await self.data_integrator.integrate_g2b_data(bid_data)
            all_cases.extend(bid_products)
        
        # 계약정보 데이터 처리
        if contract_data.get('success'):
            contract_products = await self.data_integrator.integrate_g2b_data(contract_data)
            all_cases.extend(contract_products)
        
        result = {
            'success': True,
            'total_cases': len(all_cases),
            'cases': all_cases,
            'bid_announcements': len(bid_data.get('items', [])),
            'contracts': len(contract_data.get('items', [])),
            'search_params': {
                'organization': organization,
                'date_range': date_range,
                'limit': limit
            },
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"조달 사례 검색 완료: {len(all_cases)}개 사례")
        return result

    
    async def get_market_price_analysis(
        self, 
        product_name: str,
        time_period: str = "1month"
    ) -> Dict[str, Any]:
        """시장 가격 분석"""
        logger.info(f"시장 가격 분석: {product_name}")
        

        # 여러 소스에서 가격 정보 수집
        search_results = await self.advanced_search_products(product_name)
        
        if not search_results.get('success') or not search_results.get('products'):
            return {
                'success': False,
                'error': '가격 분석을 위한 데이터가 부족합니다',
                'analysis': {}
            }
        
        products = search_results['products']
        
        # 가격 분석 수행
        analysis = self._analyze_product_prices(products, product_name)
        
        # G2B 가격 정보 추가 조회
        if self.g2b_client:
            async with self.g2b_client as client:
                price_data = await client.get_price_info({
                    'item_name': product_name,
                    'limit': 10
                })
                
                if price_data.get('success'):
                    g2b_prices = [
                        item.get('price', 0) 
                        for item in price_data.get('items', [])
                        if item.get('price', 0) > 0
                    ]
                    analysis['g2b_reference_prices'] = g2b_prices
                    if g2b_prices:
                        analysis['g2b_avg_price'] = sum(g2b_prices) / len(g2b_prices)
        
        result = {
            'success': True,
            'product_name': product_name,
            'analysis': analysis,
            'data_sources': search_results['source_counts'],
            'analysis_date': datetime.now().isoformat()
        }
        
        logger.info(f"시장 가격 분석 완료: {product_name}")
        return result
        

    
    # === 내부 헬퍼 메서드 ===
    
    async def _async_search_coupang(self, keyword: str, limit: int) -> List[UnifiedProduct]:
        """비동기 쿠팡 검색"""
        if not self.coupang_client:
            await self.initialize_clients()
        
        async with self.coupang_client as client:
            coupang_data = await client.search_products(keyword, {'limit': limit})
            return await self.data_integrator.integrate_coupang_data(coupang_data)
    
    async def _async_search_g2b(self, keyword: str, limit: int) -> List[UnifiedProduct]:
        """비동기 G2B 검색"""
        if not self.g2b_client:
            await self.initialize_clients()
        
        async with self.g2b_client as client:
            g2b_data = await client.get_bid_announcements({
                'limit': limit,
                'keyword': keyword
            })
            return await self.data_integrator.integrate_g2b_data(g2b_data)
    
    async def _async_search_all_platforms(self, keyword: str, limit_per_platform: int) -> Dict[str, List[Dict[str, Any]]]:
        """비동기 전체 플랫폼 검색 (기존 인터페이스용)"""
        coupang_products = await self._async_search_coupang(keyword, limit_per_platform)
        g2b_products = await self._async_search_g2b(keyword, limit_per_platform)
        
        return {
            "coupang": self._convert_unified_to_legacy_coupang(coupang_products),
            "g2b": self._convert_unified_to_legacy_g2b(g2b_products)
        }
    
    async def _async_search_g2b_advanced(self, keyword: str, filters: Dict[str, Any] = None) -> Dict:
        """고급 G2B 검색"""
        if not self.g2b_client:
            await self.initialize_clients()
        
        params = {
            'limit': filters.get('limit', 10) if filters else 10,
            'keyword': keyword
        }
        
        if filters:
            if filters.get('budget_min'):
                params['budget_min'] = filters['budget_min']
            if filters.get('budget_max'):
                params['budget_max'] = filters['budget_max']
            if filters.get('date_range'):
                params.update(filters['date_range'])
        
        async with self.g2b_client as client:
            return await client.get_bid_announcements(params)
    
    async def _async_search_coupang_advanced(self, keyword: str, filters: Dict[str, Any] = None) -> Dict:
        """고급 쿠팡 검색"""
        if not self.coupang_client:
            await self.initialize_clients()
        
        params = {
            'limit': filters.get('limit', 10) if filters else 10
        }
        
        if filters:
            if filters.get('budget_min'):
                params['min_price'] = filters['budget_min']
            if filters.get('budget_max'):
                params['max_price'] = filters['budget_max']
            if filters.get('category'):
                params['category'] = filters['category']
        
        async with self.coupang_client as client:
            return await client.search_products(keyword, params)
    
    def _remove_duplicates(self, products: List[UnifiedProduct], duplicate_groups: List[List[int]]) -> List[UnifiedProduct]:
        """중복 제거"""
        to_remove = set()
        
        for group in duplicate_groups:
            # 각 그룹에서 첫 번째 상품만 유지
            to_remove.update(group[1:])
        
        return [product for i, product in enumerate(products) if i not in to_remove]
    
    def _analyze_product_prices(self, products: List[UnifiedProduct], product_name: str) -> Dict[str, Any]:
        """상품 가격 분석"""
        prices = [float(product.price['amount']) for product in products if product.price['amount'] > 0]
        
        if not prices:
            return {
                'error': '분석할 가격 데이터가 없습니다',
                'price_count': 0
            }
        
        prices.sort()
        
        analysis = {
            'price_count': len(prices),
            'min_price': min(prices),
            'max_price': max(prices),
            'avg_price': sum(prices) / len(prices),
            'median_price': prices[len(prices) // 2],
            'price_range': max(prices) - min(prices),
            'price_std_dev': self._calculate_std_dev(prices)
        }
        
        # 가격대별 분포
        analysis['price_distribution'] = self._calculate_price_distribution(prices)
        
        # 소스별 가격 비교
        analysis['source_comparison'] = self._compare_prices_by_source(products)
        
        return analysis
    
    def _calculate_std_dev(self, prices: List[float]) -> float:
        """표준편차 계산"""
        if len(prices) < 2:
            return 0.0
        
        mean = sum(prices) / len(prices)
        variance = sum((x - mean) ** 2 for x in prices) / len(prices)
        return variance ** 0.5
    
    def _calculate_price_distribution(self, prices: List[float]) -> Dict[str, int]:
        """가격대별 분포 계산"""
        if not prices:
            return {}
        
        min_price = min(prices)
        max_price = max(prices)
        range_size = (max_price - min_price) / 5  # 5개 구간
        
        distribution = {}
        for i in range(5):
            range_start = min_price + (i * range_size)
            range_end = min_price + ((i + 1) * range_size)
            
            count = sum(1 for price in prices if range_start <= price < range_end)
            if i == 4:  # 마지막 구간은 최대값 포함
                count = sum(1 for price in prices if range_start <= price <= range_end)
            
            distribution[f"{range_start:.0f}-{range_end:.0f}"] = count
        
        return distribution
    
    def _compare_prices_by_source(self, products: List[UnifiedProduct]) -> Dict[str, Dict[str, float]]:
        """소스별 가격 비교"""
        by_source = {}
        
        for product in products:
            source = product.source
            price = float(product.price['amount'])
            
            if price > 0:
                if source not in by_source:
                    by_source[source] = []
                by_source[source].append(price)
        
        comparison = {}
        for source, prices in by_source.items():
            if prices:
                comparison[source] = {
                    'count': len(prices),
                    'avg_price': sum(prices) / len(prices),
                    'min_price': min(prices),
                    'max_price': max(prices)
                }
        
        return comparison
    
    def _convert_unified_to_legacy_coupang(self, products: List[UnifiedProduct]) -> List[Dict[str, Any]]:
        """UnifiedProduct를 기존 쿠팡 형식으로 변환"""
        legacy_products = []
        
        for product in products:
            if product.source == 'coupang':
                legacy_product = {
                    "platform": "coupang",
                    "product_id": product.metadata.get('product_id', product.id),
                    "name": product.name['original'],
                    "price": float(product.price['amount']),
                    "original_price": product.specifications.get('original_price', float(product.price['amount'])),
                    "discount_rate": product.specifications.get('discount_rate', 0),
                    "rating": product.specifications.get('rating', 0),
                    "review_count": product.specifications.get('review_count', 0),
                    "image_url": product.metadata.get('image_url', ''),
                    "product_url": product.metadata.get('url', ''),
                    "vendor": product.specifications.get('vendor', ''),
                    "delivery": {
                        "fee": product.specifications.get('delivery_fee', 0),
                        "free_shipping": product.specifications.get('is_free_shipping', False)
                    },
                    "collected_at": product.timestamps.get('created', datetime.now()).isoformat()
                }
                legacy_products.append(legacy_product)
        
        return legacy_products
    
    def _convert_unified_to_legacy_g2b(self, products: List[UnifiedProduct]) -> List[Dict[str, Any]]:
        """UnifiedProduct를 기존 G2B 형식으로 변환"""
        legacy_products = []
        
        for product in products:
            if product.source == 'g2b':
                legacy_product = {
                    "platform": "g2b",
                    "bid_ntce_no": product.metadata.get('announcement_number', product.id),
                    "bid_ntce_nm": product.name['original'],
                    "ntce_instt_nm": product.metadata.get('organization', ''),
                    "dmnd_instt_nm": product.metadata.get('organization', ''),
                    "bid_mtd_nm": product.specifications.get('bid_method', ''),
                    "cntrct_cncls_mtd_nm": product.specifications.get('contract_type', ''),
                    "rsrvtn_price_range": f"{float(product.price['amount']):,}원",
                    "rgst_dt": product.metadata.get('announcement_date', ''),
                    "bid_cls_dt": product.metadata.get('deadline', ''),
                    "openg_dt": product.metadata.get('deadline', ''),
                    "collected_at": product.timestamps.get('created', datetime.now()).isoformat()
                }
                legacy_products.append(legacy_product)
        
        return legacy_products
    
    
    # === 기존 헤더 생성 함수들 유지 ===
    
    def _get_coupang_headers(self, method: str, url: str, params: Dict) -> Dict[str, str]:
        """쿠팡 API 인증 헤더 생성 (기존 호환성)"""
        timestamp = str(int(time.time() * 1000))
        query_string = urlencode(params)
        
        message = f"{method} {url}?{query_string}\n{timestamp}"
        signature = hmac.new(
            (self.coupang_secret_key or "test").encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return {
            "Authorization": f"HMAC-SHA256 accesskey={self.coupang_access_key}, timestamp={timestamp}, signature={signature}",
            "Content-Type": "application/json"
        }
    
    def _parse_coupang_response(self, data: Dict) -> List[Dict[str, Any]]:
        """쿠팡 응답 데이터 파싱 (기존 호환성)"""
        products = []
        
        if "data" in data and "productData" in data["data"]:
            for item in data["data"]["productData"]:
                product = {
                    "platform": "coupang",
                    "product_id": item.get("productId"),
                    "name": item.get("productName", ""),
                    "price": item.get("productPrice", 0),
                    "original_price": item.get("productOriginalPrice", 0),
                    "discount_rate": item.get("discountRate", 0),
                    "rating": item.get("rating", 0),
                    "review_count": item.get("reviewCount", 0),
                    "image_url": item.get("productImage", ""),
                    "product_url": item.get("productUrl", ""),
                    "vendor": item.get("vendorName", ""),
                    "delivery": item.get("delivery", {}),
                    "collected_at": datetime.now().isoformat()
                }
                products.append(product)
        
        return products
    
    def _parse_g2b_response(self, data: Dict) -> List[Dict[str, Any]]:
        """나라장터 응답 데이터 파싱 (기존 호환성)"""
        products = []
        
        if "response" in data and "body" in data["response"]:
            items = data["response"]["body"].get("items", [])
            
            for item in items:
                product = {
                    "platform": "g2b",
                    "bid_ntce_no": item.get("bidNtceNo"),
                    "bid_ntce_nm": item.get("bidNtceNm", ""),
                    "ntce_instt_nm": item.get("ntceInsttNm", ""),
                    "dmnd_instt_nm": item.get("dmndInsttNm", ""),
                    "bid_mtd_nm": item.get("bidMtdNm", ""),
                    "cntrct_cncls_mtd_nm": item.get("cntrctCnclsMtdNm", ""),
                    "rsrvtn_price_range": item.get("rsrvtnPriceRange", ""),
                    "rgst_dt": item.get("rgstDt", ""),
                    "bid_cls_dt": item.get("bidClsDt", ""),
                    "openg_dt": item.get("opengDt", ""),
                    "collected_at": datetime.now().isoformat()
                }
                products.append(product)
        
        return products
    
    def run_validation_tests(self) -> bool:
        """모듈 검증 테스트"""
        test_cases = [
            {
                "input": {"keyword": "테스트", "limit": 3},
                "expected": None
            }
        ]
        
        def test_search_function(keyword: str, limit: int):
            coupang_results = self.search_coupang_products(keyword, limit)
            g2b_results = self.search_g2b_products(keyword, limit)
            return len(coupang_results) > 0 or len(g2b_results) > 0
        
        validation_result = self.validator.validate_function(test_search_function, test_cases)
        
        debug_info = self.validator.debug_module_state(self)
        summary = self.validator.get_test_summary()
        
        logger.info(f"DataCollectorModule validation summary: {summary}")
        
        return validation_result

# 디버그 실행
if __name__ == "__main__":
    async def main():
        logger.info("업데이트된 DataCollectorModule 디버그 모드 시작")
        
        collector = DataCollectorModule()
        await collector.initialize_clients()
        
        # 기존 인터페이스 테스트
        test_keyword = "사무용 의자"
        
        # 기존 검색 방식 테스트
        coupang_products = collector.search_coupang_products(test_keyword, 3)
        logger.info(f"기존 쿠팡 검색 결과: {len(coupang_products)}개")
        
        g2b_products = collector.search_g2b_products(test_keyword, 3)
        logger.info(f"기존 나라장터 검색 결과: {len(g2b_products)}개")
        
        # 새로운 고급 검색 테스트
        advanced_results = await collector.advanced_search_products(
            test_keyword,
            filters={'limit': 10, 'budget_min': 100000, 'budget_max': 1000000}
        )
        logger.info(f"고급 검색 결과: {advanced_results.get('total_count', 0)}개")
        
        # 시장 가격 분석 테스트
        price_analysis = await collector.get_market_price_analysis(test_keyword)
        logger.info(f"가격 분석 결과: {price_analysis.get('success', False)}")
        
        # 조달 사례 검색 테스트
        procurement_cases = await collector.search_procurement_cases(limit=5)
        logger.info(f"조달 사례 검색 결과: {procurement_cases.get('total_cases', 0)}개")
        
        # 검증 테스트
        if collector.run_validation_tests():
            logger.info("모든 검증 테스트 통과")
        else:
            logger.error("검증 테스트 실패")
        
        logger.info("업데이트된 DataCollectorModule 디버그 완료")
    
    asyncio.run(main())
