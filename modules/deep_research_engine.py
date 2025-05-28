"""
딥리서치 엔진 - 조달 분석을 위한 종합적 시장 조사 시스템
상황에 따라 다른 딥리서치 전략을 적용할 수 있는 모듈화된 구조
"""

import asyncio
import json
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from utils import get_logger

logger = get_logger(__name__)

class ResearchDepth(Enum):
    """리서치 깊이 레벨"""
    BASIC = "basic"          # 기본 검색만
    STANDARD = "standard"    # 표준 분석 (기본값)
    COMPREHENSIVE = "comprehensive"  # 종합 분석
    ENTERPRISE = "enterprise"        # 기업급 심화 분석

class ResearchFocus(Enum):
    """리서치 집중 영역"""
    PRICE_FOCUSED = "price"      # 가격 중심 분석
    QUALITY_FOCUSED = "quality"  # 품질 중심 분석
    SUPPLIER_FOCUSED = "supplier" # 공급업체 중심 분석
    RISK_FOCUSED = "risk"        # 리스크 중심 분석
    BALANCED = "balanced"        # 균형 분석 (기본값)

@dataclass
class ResearchConfig:
    """딥리서치 설정"""
    depth: ResearchDepth = ResearchDepth.STANDARD
    focus: ResearchFocus = ResearchFocus.BALANCED
    max_products: int = 50
    max_suppliers: int = 10
    max_similar_cases: int = 10
    price_history_months: int = 12
    enable_real_time_data: bool = True
    enable_rag_search: bool = True
    enable_vector_search: bool = True
    timeout_seconds: int = 30

@dataclass
class DeepResearchResult:
    """딥리서치 결과 데이터"""
    market_analysis: Dict[str, Any]
    price_trends: List[Dict]
    competitor_analysis: List[Dict]
    supplier_evaluation: List[Dict]
    risk_assessment: Dict[str, Any]
    recommendations: List[str]
    confidence_score: float
    research_config: ResearchConfig = None
    execution_time: float = 0.0
    data_sources: List[str] = None

    def __post_init__(self):
        if self.research_config is None:
            self.research_config = ResearchConfig()
        if self.data_sources is None:
            self.data_sources = []

class DeepResearchEngine(ABC):
    """딥리서치 엔진 추상 클래스"""
    
    def __init__(self, config: ResearchConfig = None):
        self.config = config or ResearchConfig()
        self.start_time = None
        self.data_sources = []
        
    @abstractmethod
    async def conduct_research(self, request_data: Dict[str, Any]) -> DeepResearchResult:
        """메인 리서치 실행"""
        pass
    
    @abstractmethod
    async def analyze_market_conditions(self, request_data: Dict) -> Dict[str, Any]:
        """시장 상황 분석"""
        pass
    
    @abstractmethod
    async def evaluate_suppliers(self, request_data: Dict) -> List[Dict]:
        """공급업체 평가"""
        pass
    
    @abstractmethod
    async def perform_risk_analysis(self, request_data: Dict, market_data: Dict) -> Dict[str, Any]:
        """리스크 분석"""
        pass

class DefaultDeepResearchEngine(DeepResearchEngine):
    """기본 딥리서치 엔진 구현"""
    
    def __init__(self, config: ResearchConfig = None):
        super().__init__(config)
        self._initialize_modules()
    
    def _initialize_modules(self):
        """모듈 초기화"""
        try:
            self.rag_module = None
            self.vector_db = None
            self.coupang_api = None
            self.g2b_api = None
            
            logger.debug("딥리서치 엔진 모듈 초기화 완료")
            
        except Exception as e:
            logger.error(f"모듈 초기화 실패: {e}")
    
    async def conduct_research(self, request_data: Dict[str, Any]) -> DeepResearchResult:
        """메인 딥리서치 실행"""
        self.start_time = asyncio.get_event_loop().time()
        self.data_sources = []
        
        logger.info(f"딥리서치 시작 - 깊이: {self.config.depth.value}, 집중: {self.config.focus.value}")
        
        try:
            # 시장 분석
            market_data = await self.analyze_market_conditions(request_data)
            
            # 가격 동향 분석
            price_trends = await self._analyze_price_trends(request_data)
            
            # 공급업체 평가
            suppliers = await self.evaluate_suppliers(request_data)
            
            # 리스크 분석
            risks = await self.perform_risk_analysis(request_data, market_data)
            
            # 경쟁사 분석
            competitors = self._analyze_competitors(market_data)
            
            # 추천사항 생성
            recommendations = self._generate_recommendations(
                market_data, suppliers, risks, self.config.focus
            )
            
            # 신뢰도 점수 계산
            confidence_score = self._calculate_confidence_score(
                market_data, len(suppliers), len(self.data_sources)
            )
            
            execution_time = asyncio.get_event_loop().time() - self.start_time
            
            logger.info(f"딥리서치 완료 - 실행시간: {execution_time:.2f}초, 신뢰도: {confidence_score:.1%}")
            
            return DeepResearchResult(
                market_analysis=market_data,
                price_trends=price_trends,
                competitor_analysis=competitors,
                supplier_evaluation=suppliers,
                risk_assessment=risks,
                recommendations=recommendations,
                confidence_score=confidence_score,
                research_config=self.config,
                execution_time=execution_time,
                data_sources=self.data_sources
            )
            
        except Exception as e:
            logger.error(f"딥리서치 실행 실패: {e}")
            raise e
    
    async def analyze_market_conditions(self, request_data: Dict) -> Dict[str, Any]:
        """시장 상황 분석"""
        logger.debug("시장 상황 분석 중")
        
        market_data = {
            'total_products': 25,
            'supplier_count': 8,
            'price_range': {
                'min': 150000,
                'max': 300000,
                'avg': 220000,
                'recommended': 200000
            },
            'market_trend': '안정적 시장',
            'competition_level': '보통',
        }
        
        return market_data
    
    async def evaluate_suppliers(self, request_data: Dict) -> List[Dict]:
        """공급업체 평가"""
        logger.debug("공급업체 평가 중")
        
        return self._generate_mock_suppliers()
    
    async def perform_risk_analysis(self, request_data: Dict, market_data: Dict) -> Dict[str, Any]:
        """리스크 분석"""
        logger.debug("리스크 분석 중")
        
        risks = {
            'budget_risk': self._assess_budget_risk(request_data, market_data),
            'supply_risk': self._assess_supply_risk(market_data),
            'quality_risk': self._assess_quality_risk(request_data),
            'delivery_risk': self._assess_delivery_risk(request_data),
            'market_risk': self._assess_market_risk(market_data)
        }
        
        # 전체 리스크 레벨 계산
        risk_scores = [risk['level'] for risk in risks.values()]
        overall_risk = sum(risk_scores) / len(risk_scores)
        
        risks['overall'] = {
            'level': overall_risk,
            'category': self._categorize_risk_level(overall_risk),
            'mitigation_strategies': self._generate_mitigation_strategies(risks)
        }
        
        return risks
    
    async def _analyze_price_trends(self, request_data: Dict) -> List[Dict]:
        """가격 동향 분석"""
        price_trends = []
        
        for i in range(12):
            date = datetime.now() - timedelta(days=30*i)
            price_trends.append({
                'date': date.strftime('%Y-%m'),
                'price': 200000 + (i * 5000),
                'change_rate': round((i * 0.5), 1)
            })
        
        return price_trends
    
    def _analyze_competitors(self, market_data: Dict) -> List[Dict]:
        """경쟁사 분석"""
        competitors = [
            {
                'name': '경쟁업체 A',
                'product_count': 15,
                'avg_price': 180000,
                'avg_rating': 4.2
            },
            {
                'name': '경쟁업체 B', 
                'product_count': 12,
                'avg_price': 220000,
                'avg_rating': 4.5
            }
        ]
        
        return competitors
    
    def _assess_budget_risk(self, request_data: Dict, market_data: Dict) -> Dict[str, Any]:
        """예산 리스크 평가"""
        try:
            requested_budget = int(str(request_data.get('예상단가', '0')).replace(',', '').replace('원', ''))
            market_avg = market_data.get('price_range', {}).get('avg', 0)
            
            if requested_budget == 0 or market_avg == 0:
                return {'level': 2, 'description': '예산 정보 부족으로 평가 어려움'}
            
            ratio = requested_budget / market_avg
            
            if ratio >= 1.2:
                return {'level': 1, 'description': '예산이 시장 평균보다 20% 이상 높아 안전함'}
            elif ratio >= 0.9:
                return {'level': 2, 'description': '예산이 시장 평균 수준으로 적정함'}
            else:
                return {'level': 4, 'description': '예산이 시장 평균보다 낮아 품질 저하 우려'}
                
        except Exception as e:
            logger.warning(f"예산 리스크 평가 실패: {e}")
            return {'level': 2, 'description': '평가 중 오류 발생'}
    
    def _assess_supply_risk(self, market_data: Dict) -> Dict[str, Any]:
        """공급 리스크 평가"""
        supplier_count = market_data.get('supplier_count', 0)
        
        if supplier_count >= 10:
            return {'level': 1, 'description': '충분한 공급업체로 안정적 공급 가능'}
        elif supplier_count >= 5:
            return {'level': 2, 'description': '적정 수준의 공급업체 확보'}
        elif supplier_count >= 2:
            return {'level': 3, 'description': '제한적 공급업체로 주의 필요'}
        else:
            return {'level': 4, 'description': '공급업체 부족으로 높은 리스크'}
    
    def _assess_quality_risk(self, request_data: Dict) -> Dict[str, Any]:
        """품질 리스크 평가"""
        specifications = request_data.get('규격', '')
        
        if len(specifications) > 100:
            return {'level': 2, 'description': '상세한 사양으로 품질 관리 가능'}
        elif len(specifications) > 20:
            return {'level': 3, 'description': '기본 사양 제시로 추가 검토 필요'}
        else:
            return {'level': 4, 'description': '사양 불명확으로 품질 리스크 높음'}
    
    def _assess_delivery_risk(self, request_data: Dict) -> Dict[str, Any]:
        """납기 리스크 평가"""
        urgency = request_data.get('긴급도', '보통')
        
        if urgency == '매우높음':
            return {'level': 4, 'description': '매우 급한 납기로 높은 리스크'}
        elif urgency == '높음':
            return {'level': 3, 'description': '급한 납기로 주의 필요'}
        else:
            return {'level': 2, 'description': '일반적인 납기 리스크 수준'}
    
    def _assess_market_risk(self, market_data: Dict) -> Dict[str, Any]:
        """시장 리스크 평가"""
        trend = market_data.get('market_trend', '')
        
        if trend == "활발한 시장":
            return {'level': 1, 'description': '안정적이고 활발한 시장'}
        elif trend == "안정적 시장":
            return {'level': 2, 'description': '보통 수준의 시장 안정성'}
        else:
            return {'level': 3, 'description': '제한적 시장으로 주의 필요'}
    
    def _categorize_risk_level(self, level: float) -> str:
        """리스크 레벨 분류"""
        if level <= 2:
            return "낮음"
        elif level <= 3:
            return "보통"
        else:
            return "높음"
    
    def _generate_mitigation_strategies(self, risks: Dict) -> List[str]:
        """리스크 완화 전략 생성"""
        strategies = []
        
        for risk_type, risk_data in risks.items():
            if risk_type == 'overall':
                continue
                
            level = risk_data.get('level', 0)
            if level >= 3:
                if risk_type == 'budget_risk':
                    strategies.append("예산 재검토 및 추가 확보 검토")
                elif risk_type == 'supply_risk':
                    strategies.append("다양한 공급업체 발굴 및 계약 다변화")
                elif risk_type == 'quality_risk':
                    strategies.append("품질 사양 명확화 및 검수 기준 강화")
                elif risk_type == 'delivery_risk':
                    strategies.append("납기 일정 여유분 확보 및 대체 공급망 준비")
        
        if not strategies:
            strategies.append("현재 리스크 수준은 관리 가능한 범위입니다")
        
        return strategies
    
    def _generate_recommendations(self, market_data: Dict, suppliers: List[Dict], 
                                risks: Dict, focus: ResearchFocus) -> List[str]:
        """집중 영역별 맞춤 추천사항 생성"""
        recommendations = []
        
        if market_data.get('total_products', 0) > 30:
            recommendations.append("활발한 시장으로 충분한 선택권 확보")
        
        if suppliers and len(suppliers) > 0:
            top_supplier = suppliers[0]
            recommendations.append(f"최고 평가 공급업체: {top_supplier.get('name', 'N/A')} (점수: {top_supplier.get('overall_score', 0):.1f})")
        
        if focus == ResearchFocus.PRICE_FOCUSED:
            price_range = market_data.get('price_range', {})
            if price_range.get('recommended'):
                recommendations.append(f"권장 구매 가격: {price_range['recommended']:,}원")
        
        elif focus == ResearchFocus.QUALITY_FOCUSED:
            recommendations.append("품질 사양 명확화 및 검수 기준 수립 권장")
        
        elif focus == ResearchFocus.SUPPLIER_FOCUSED:
            recommendations.append("다수 공급업체와 협상을 통한 최적 조건 확보")
        
        elif focus == ResearchFocus.RISK_FOCUSED:
            overall_risk = risks.get('overall', {}).get('category', '보통')
            recommendations.append(f"전체 리스크 수준: {overall_risk} - 지속적 모니터링 필요")
        
        if risks.get('overall', {}).get('level', 3) >= 3:
            recommendations.append("주요 리스크 요인 해결 후 진행 권장")
        
        return recommendations
    
    def _calculate_confidence_score(self, market_data: Dict, supplier_count: int, 
                                  data_source_count: int) -> float:
        """신뢰도 점수 계산"""
        base_score = 0.5
        
        product_count = market_data.get('total_products', 0)
        if product_count > 50:
            base_score += 0.2
        elif product_count > 20:
            base_score += 0.1
        
        if supplier_count > 5:
            base_score += 0.15
        elif supplier_count > 2:
            base_score += 0.1
        
        if data_source_count > 3:
            base_score += 0.15
        elif data_source_count > 1:
            base_score += 0.1
        
        return min(base_score, 1.0)
    
    def _generate_mock_suppliers(self) -> List[Dict]:
        """모조 공급업체 데이터 생성"""
        mock_suppliers = [
            {
                'name': '테스트 공급업체 A',
                'evaluation': {
                    '가격 경쟁력': 4.2,
                    '품질 신뢰도': 4.5,
                    '납기 준수율': 4.0,
                    '사후서비스': 3.8,
                    '재무 안정성': 4.1,
                    '기술 역량': 3.9
                },
                'overall_score': 4.08,
                'contact_info': {'phone': '02-1234-5678'},
                'specialization': ['IT장비', '사무용품']
            },
            {
                'name': '테스트 공급업체 B',
                'evaluation': {
                    '가격 경쟁력': 4.5,
                    '품질 신뢰도': 3.8,
                    '납기 준수율': 4.2,
                    '사후서비스': 4.0,
                    '재무 안정성': 3.7,
                    '기술 역량': 4.1
                },
                'overall_score': 4.05,
                'contact_info': {'phone': '02-2345-6789'},
                'specialization': ['전자기기']
            }
        ]
        
        return mock_suppliers

# 팩토리 클래스
class DeepResearchEngineFactory:
    """딥리서치 엔진 팩토리"""
    
    _engines = {
        'default': DefaultDeepResearchEngine
    }
    
    @classmethod
    def create_engine(cls, engine_type: str = 'default', 
                     config: ResearchConfig = None) -> DeepResearchEngine:
        """딥리서치 엔진 생성"""
        engine_class = cls._engines.get(engine_type, DefaultDeepResearchEngine)
        
        if config:
            return engine_class(config)
        else:
            return engine_class()
    
    @classmethod
    def get_available_engines(cls) -> List[str]:
        """사용 가능한 엔진 목록"""
        return list(cls._engines.keys())
