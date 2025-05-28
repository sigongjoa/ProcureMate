from .core import DeepResearchCore
from .config import ResearchConfig, ResearchFocus, ResearchDepth

class PriceFocusedStrategy(DeepResearchCore):
    def __init__(self):
        config = ResearchConfig(
            focus=ResearchFocus.PRICE_FOCUSED,
            depth=ResearchDepth.COMPREHENSIVE,
            max_products=100
        )
        super().__init__(config)
    
    def _generate_recommendations(self, market_data, suppliers, risks):
        recommendations = super()._generate_recommendations(market_data, suppliers, risks)
        
        price_range = market_data.get('price_range', {})
        if price_range.get('avg', 0) > 0:
            savings = int(price_range['avg'] * 0.15)
            recommendations.append(f"가격 협상을 통해 최대 {savings:,}원 절약 가능")
        
        return recommendations

class QualityFocusedStrategy(DeepResearchCore):
    def __init__(self):
        config = ResearchConfig(
            focus=ResearchFocus.QUALITY_FOCUSED,
            depth=ResearchDepth.COMPREHENSIVE
        )
        super().__init__(config)
    
    async def _evaluate_suppliers(self, request_data):
        suppliers = await super()._evaluate_suppliers(request_data)
        
        # 품질 가중치 적용
        for supplier in suppliers:
            quality_score = supplier['evaluation'].get('품질 신뢰도', 3.5)
            supplier['evaluation']['품질 신뢰도'] = min(quality_score * 1.2, 5.0)
            
            # 재계산
            scores = supplier['evaluation'].values()
            supplier['overall_score'] = sum(scores) / len(scores)
        
        suppliers.sort(key=lambda x: x['overall_score'], reverse=True)
        return suppliers

class RiskFocusedStrategy(DeepResearchCore):
    def __init__(self):
        config = ResearchConfig(
            focus=ResearchFocus.RISK_FOCUSED,
            depth=ResearchDepth.ENTERPRISE
        )
        super().__init__(config)
    
    def _assess_risks(self, request_data, market_data):
        risks = super()._assess_risks(request_data, market_data)
        
        # 추가 리스크 요인
        risks['regulatory_risk'] = {'level': 2, 'description': '규제 준수 리스크'}
        risks['technology_risk'] = {'level': 2, 'description': '기술 변화 리스크'}
        
        # 전체 리스크 재계산
        risk_levels = [risk['level'] for key, risk in risks.items() if key != 'overall']
        overall_risk = sum(risk_levels) / len(risk_levels)
        risks['overall']['level'] = overall_risk
        
        return risks

class SupplierFocusedStrategy(DeepResearchCore):
    def __init__(self):
        config = ResearchConfig(
            focus=ResearchFocus.SUPPLIER_FOCUSED,
            max_suppliers=20
        )
        super().__init__(config)
    
    async def _evaluate_suppliers(self, request_data):
        suppliers = await super()._evaluate_suppliers(request_data)
        
        # 공급업체 추가 정보
        for supplier in suppliers:
            supplier['additional_info'] = {
                'market_share': '5-10%',
                'years_in_business': '10+',
                'specialization': ['IT장비', '사무용품']
            }
        
        return suppliers

class BalancedStrategy(DeepResearchCore):
    def __init__(self):
        config = ResearchConfig(focus=ResearchFocus.BALANCED)
        super().__init__(config)
