import asyncio
import logging
from typing import Dict, List, Any
from datetime import datetime
from .config import ResearchConfig, ResearchFocus

logger = logging.getLogger(__name__)

class DeepResearchResult:
    def __init__(self, market_analysis: Dict, price_trends: List, 
                 supplier_evaluation: List, risk_assessment: Dict,
                 recommendations: List, confidence_score: float,
                 execution_time: float, data_sources: List):
        self.market_analysis = market_analysis
        self.price_trends = price_trends
        self.supplier_evaluation = supplier_evaluation
        self.risk_assessment = risk_assessment
        self.recommendations = recommendations
        self.confidence_score = confidence_score
        self.execution_time = execution_time
        self.data_sources = data_sources

class DeepResearchCore:
    def __init__(self, config: ResearchConfig = None):
        self.config = config or ResearchConfig()
        self.start_time = None
        self.data_sources = []
        self._initialize_modules()
    
    def _initialize_modules(self):
        try:
            from modules.coupang_api_client import CoupangApiClient
            from modules.g2b_api_client import G2BApiClient
            from modules.advanced_rag_module import AdvancedRAGModule
            
            self.coupang_api = CoupangApiClient() if self.config.enable_real_time_data else None
            self.g2b_api = G2BApiClient() if self.config.enable_real_time_data else None
            self.rag_module = AdvancedRAGModule() if self.config.enable_rag_search else None
        except Exception as e:
            logger.error(f"모듈 초기화 실패: {e}")
            self.coupang_api = None
            self.g2b_api = None
            self.rag_module = None
    
    async def conduct_research(self, request_data: Dict[str, Any]) -> DeepResearchResult:
        self.start_time = datetime.now()
        self.data_sources = []
        
        logger.info(f"딥리서치 시작 - {self.config.focus.value}")
        
        # 병렬 데이터 수집
        market_data = await self._collect_market_data(request_data)
        suppliers = await self._evaluate_suppliers(request_data)
        risks = self._assess_risks(request_data, market_data)
        recommendations = self._generate_recommendations(market_data, suppliers, risks)
        
        execution_time = (datetime.now() - self.start_time).total_seconds()
        confidence_score = self._calculate_confidence(market_data, suppliers)
        
        logger.info(f"딥리서치 완료 - {execution_time:.2f}초")
        
        return DeepResearchResult(
            market_analysis=market_data,
            price_trends=[],
            supplier_evaluation=suppliers,
            risk_assessment=risks,
            recommendations=recommendations,
            confidence_score=confidence_score,
            execution_time=execution_time,
            data_sources=self.data_sources
        )
    
    async def _collect_market_data(self, request_data: Dict) -> Dict[str, Any]:
        product_name = request_data.get('품명', '')
        market_data = {
            'total_products': 0,
            'supplier_count': 0,
            'price_range': {'min': 0, 'max': 0, 'avg': 0, 'recommended': 0},
            'market_trend': '분석 중',
            'competition_level': '보통'
        }
        
        if not self.config.enable_real_time_data:
            return market_data
        
        # Coupang 데이터 수집
        coupang_data = []
        if self.coupang_api:
            try:
                result = await asyncio.wait_for(
                    self.coupang_api.search_products(query=product_name, limit=self.config.max_products),
                    timeout=self.config.timeout_seconds
                )
                if result.get('success'):
                    coupang_data = result['data']
                    self.data_sources.append('coupang')
            except Exception as e:
                logger.warning(f"Coupang API 오류: {e}")
        
        # G2B 데이터 수집
        g2b_data = []
        if self.g2b_api:
            try:
                result = await asyncio.wait_for(
                    self.g2b_api.search_announcements(keyword=product_name, numOfRows=self.config.max_products),
                    timeout=self.config.timeout_seconds
                )
                if result.get('success'):
                    g2b_data = result['data']
                    self.data_sources.append('g2b')
            except Exception as e:
                logger.warning(f"G2B API 오류: {e}")
        
        # 데이터 분석
        all_products = coupang_data + g2b_data
        market_data['total_products'] = len(all_products)
        market_data['price_range'] = self._calculate_price_range(all_products)
        market_data['supplier_count'] = len(set([p.get('supplier', '') for p in coupang_data]))
        market_data['market_trend'] = self._determine_trend(len(all_products))
        
        return market_data
    
    async def _evaluate_suppliers(self, request_data: Dict) -> List[Dict]:
        suppliers = []
        
        if not self.rag_module:
            return self._mock_suppliers()
        
        try:
            query = f"{request_data.get('품명', '')} 공급업체 평가"
            result = await self.rag_module.advanced_search_with_context(query=query, max_results=self.config.max_suppliers)
            
            for supplier_data in result.get('suppliers', []):
                evaluation = {
                    '가격 경쟁력': supplier_data.get('price_score', 3.5),
                    '품질 신뢰도': supplier_data.get('quality_score', 3.5),
                    '납기 준수율': supplier_data.get('delivery_score', 3.5)
                }
                
                suppliers.append({
                    'name': supplier_data.get('name', '미확인'),
                    'evaluation': evaluation,
                    'overall_score': sum(evaluation.values()) / len(evaluation)
                })
            
            suppliers.sort(key=lambda x: x['overall_score'], reverse=True)
            self.data_sources.append('rag_suppliers')
            
        except Exception as e:
            logger.warning(f"공급업체 평가 오류: {e}")
            suppliers = self._mock_suppliers()
        
        return suppliers[:self.config.max_suppliers]
    
    def _assess_risks(self, request_data: Dict, market_data: Dict) -> Dict[str, Any]:
        budget = self._parse_budget(request_data.get('예상단가', '0'))
        market_avg = market_data.get('price_range', {}).get('avg', 0)
        
        budget_risk = 2 if budget == 0 or market_avg == 0 else (1 if budget >= market_avg * 1.2 else (4 if budget < market_avg * 0.8 else 2))
        supply_risk = 1 if market_data.get('supplier_count', 0) >= 10 else (3 if market_data.get('supplier_count', 0) >= 5 else 4)
        quality_risk = 2 if len(request_data.get('규격', '')) > 50 else 3
        
        overall_risk = (budget_risk + supply_risk + quality_risk) / 3
        
        return {
            'budget_risk': {'level': budget_risk, 'description': '예산 리스크'},
            'supply_risk': {'level': supply_risk, 'description': '공급 리스크'},
            'quality_risk': {'level': quality_risk, 'description': '품질 리스크'},
            'overall': {'level': overall_risk, 'category': '낮음' if overall_risk <= 2 else ('보통' if overall_risk <= 3 else '높음')}
        }
    
    def _generate_recommendations(self, market_data: Dict, suppliers: List, risks: Dict) -> List[str]:
        recommendations = []
        
        if market_data.get('total_products', 0) > 30:
            recommendations.append("활발한 시장으로 충분한 선택권 확보")
        
        if suppliers:
            top_supplier = suppliers[0]
            recommendations.append(f"최고 평가 공급업체: {top_supplier['name']} (점수: {top_supplier['overall_score']:.1f})")
        
        if self.config.focus == ResearchFocus.PRICE_FOCUSED:
            price_range = market_data.get('price_range', {})
            if price_range.get('recommended'):
                recommendations.append(f"권장 구매 가격: {price_range['recommended']:,}원")
        
        overall_risk = risks.get('overall', {}).get('category', '보통')
        if overall_risk == '높음':
            recommendations.append("주요 리스크 요인 해결 후 진행 권장")
        
        return recommendations
    
    def _calculate_price_range(self, products: List[Dict]) -> Dict[str, int]:
        if not products:
            return {'min': 0, 'max': 0, 'avg': 0, 'recommended': 0}
        
        prices = [p.get('price', 0) for p in products if p.get('price', 0) > 0]
        if not prices:
            return {'min': 0, 'max': 0, 'avg': 0, 'recommended': 0}
        
        min_price, max_price = min(prices), max(prices)
        avg_price = sum(prices) // len(prices)
        recommended = int(avg_price * (0.85 if self.config.focus == ResearchFocus.PRICE_FOCUSED else 0.9))
        
        return {'min': min_price, 'max': max_price, 'avg': avg_price, 'recommended': recommended}
    
    def _determine_trend(self, product_count: int) -> str:
        if product_count > 50:
            return "활발한 시장"
        elif product_count > 20:
            return "안정적 시장"
        else:
            return "제한적 시장"
    
    def _parse_budget(self, budget_str: str) -> int:
        try:
            return int(str(budget_str).replace(',', '').replace('원', ''))
        except:
            return 0
    
    def _calculate_confidence(self, market_data: Dict, suppliers: List) -> float:
        score = 0.5
        if market_data.get('total_products', 0) > 50:
            score += 0.2
        if len(suppliers) > 5:
            score += 0.15
        if len(self.data_sources) > 2:
            score += 0.15
        return min(score, 1.0)
    
    def _mock_suppliers(self) -> List[Dict]:
        return [
            {
                'name': '테스트 공급업체 A',
                'evaluation': {'가격 경쟁력': 4.2, '품질 신뢰도': 4.5, '납기 준수율': 4.0},
                'overall_score': 4.23
            },
            {
                'name': '테스트 공급업체 B',
                'evaluation': {'가격 경쟁력': 4.5, '품질 신뢰도': 3.8, '납기 준수율': 4.2},
                'overall_score': 4.17
            }
        ]
