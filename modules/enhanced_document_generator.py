import asyncio
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from utils import get_logger, prompt_loader
import matplotlib.pyplot as plt
import pandas as pd
from io import BytesIO
import base64

# 딥리서치 엔진 관련 import
from .deep_research_engine import (
    DeepResearchResult,
    ResearchConfig,
    DeepResearchEngineFactory
)

logger = get_logger(__name__)

class EnhancedDocumentGenerator:
    """딥리서치 기반 고급 문서 생성기"""
    
    def __init__(self, research_engine_type: str = 'default', research_config: dict = None):
        logger.info("EnhancedDocumentGenerator 초기화")
        
        try:
            from modules.llm_module import LlmModule
            
            self.llm_module = LlmModule()
            
            # 딥리서치 엔진 설정
            if research_config:
                config = ResearchConfig(**research_config)
            else:
                config = ResearchConfig()
            
            self.research_engine = DeepResearchEngineFactory.create_engine(
                engine_type=research_engine_type,
                config=config
            )
            
            logger.info(f"딥리서치 엔진 초기화: {research_engine_type}")
            
        except Exception as e:
            logger.error(f"모듈 로드 실패: {e}")
            raise e
    
    async def generate_comprehensive_procurement_document(
        self, 
        request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """종합 조달 문서 생성"""
        logger.info("종합 조달 문서 생성 시작")
        
        # 1. 딥리서치 수행 (새로운 엔진 사용)
        research_result = await self.research_engine.conduct_research(request_data)
        
        # 2. 비즈니스 문서 생성
        document = await self._generate_business_document({
            'request': request_data,
            'research': research_result
        })
        
        logger.info("종합 조달 문서 생성 완료")
        return document
    
    async def _conduct_deep_research(self, request_data: Dict) -> DeepResearchResult:
        """딥리서치 수행 (새로운 엔진 사용)"""
        return await self.research_engine.conduct_research(request_data)
    
    async def _analyze_market_conditions(self, request_data: Dict) -> Dict[str, Any]:
        """시장 상황 분석 (새로운 엔진 사용)"""
        return await self.research_engine.analyze_market_conditions(request_data)
    
    async def _generate_business_document(self, data: Dict) -> Dict[str, Any]:
        """비즈니스 문서 생성"""
        logger.debug("비즈니스 문서 생성 중")
        
        research_result = data.get('research')
        
        # HTML 템플릿 기반 문서 생성
        html_content = await self._create_html_document(data)
        
        # 차트 및 그래프 생성
        charts = await self._generate_charts(research_result)
        
        # 요약 보고서 생성
        executive_summary = await self._generate_executive_summary(data)
        
        # 상세 분석 보고서
        detailed_analysis = await self._generate_detailed_analysis(data)
        
        document = {
            'html_content': html_content,
            'charts': charts,
            'executive_summary': executive_summary,
            'detailed_analysis': detailed_analysis,
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'document_type': 'comprehensive_procurement_analysis',
                'confidence_score': research_result.confidence_score if research_result else 0.8,
                'data_sources': research_result.data_sources if research_result else [],
                'execution_time': research_result.execution_time if research_result else 0.0
            }
        }
        
        return document
    
    async def _create_html_document(self, data: Dict) -> str:
        """HTML 문서 생성"""
        html_template = '''
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>조달 분석 보고서</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; margin: 0; padding: 20px; background: #f8f9fa; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        .header { text-align: center; margin-bottom: 40px; padding-bottom: 20px; border-bottom: 3px solid #007bff; }
        .header h1 { color: #007bff; font-size: 2.5rem; margin: 0; }
        .header .subtitle { color: #6c757d; font-size: 1.1rem; margin-top: 10px; }
        .section { margin: 40px 0; }
        .section h2 { color: #343a40; font-size: 1.8rem; border-left: 5px solid #007bff; padding-left: 20px; }
        .section h3 { color: #495057; font-size: 1.4rem; margin-top: 30px; }
        .info-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 20px 0; }
        .info-card { background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #28a745; }
        .info-card h4 { margin: 0 0 10px 0; color: #28a745; }
        .table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        .table th, .table td { padding: 12px; text-align: left; border-bottom: 1px solid #dee2e6; }
        .table th { background: #007bff; color: white; }
        .table tr:hover { background: #f8f9fa; }
        .alert { padding: 15px; margin: 20px 0; border-radius: 5px; }
        .alert-info { background: #d1ecf1; border: 1px solid #bee5eb; color: #0c5460; }
        .alert-warning { background: #fff3cd; border: 1px solid #ffeaa7; color: #856404; }
        .alert-success { background: #d4edda; border: 1px solid #c3e6cb; color: #155724; }
        .chart-container { text-align: center; margin: 30px 0; }
        .risk-meter { display: inline-block; width: 100px; height: 100px; border-radius: 50%; position: relative; margin: 10px; }
        .risk-low { background: conic-gradient(from 0deg, #28a745 0deg 120deg, #e9ecef 120deg 360deg); }
        .risk-medium { background: conic-gradient(from 0deg, #ffc107 0deg 180deg, #e9ecef 180deg 360deg); }
        .risk-high { background: conic-gradient(from 0deg, #dc3545 0deg 240deg, #e9ecef 240deg 360deg); }
        .footer { text-align: center; margin-top: 50px; padding-top: 20px; border-top: 1px solid #dee2e6; color: #6c757d; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>조달 분석 보고서</h1>
            <div class="subtitle">AI 기반 종합 시장 분석 및 구매 권고</div>
            <div style="margin-top: 15px; color: #007bff;">생성일시: {generated_time}</div>
        </div>
        
        <div class="section">
            <h2>📋 조달 요청 정보</h2>
            <div class="info-grid">
                <div class="info-card">
                    <h4>품명</h4>
                    <p>{product_name}</p>
                </div>
                <div class="info-card">
                    <h4>규격</h4>
                    <p>{specifications}</p>
                </div>
                <div class="info-card">
                    <h4>수량</h4>
                    <p>{quantity}</p>
                </div>
                <div class="info-card">
                    <h4>예상단가</h4>
                    <p>{budget}</p>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>📊 시장 분석 결과</h2>
            <div class="alert alert-info">
                <strong>시장 현황:</strong> 총 {total_products}개 제품 분석, {supplier_count}개 공급업체 확인
            </div>
            
            <h3>가격 분석</h3>
            <table class="table">
                <thead>
                    <tr><th>구분</th><th>최저가</th><th>평균가</th><th>최고가</th><th>권장가</th></tr>
                </thead>
                <tbody>
                    <tr>
                        <td>시장 가격</td>
                        <td>{min_price:,}원</td>
                        <td>{avg_price:,}원</td>
                        <td>{max_price:,}원</td>
                        <td>{recommended_price:,}원</td>
                    </tr>
                </tbody>
            </table>
            
            <div class="chart-container">
                <img src="data:image/png;base64,{price_chart}" alt="가격 분석 차트" style="max-width: 100%; height: auto;">
            </div>
        </div>
        
        <div class="section">
            <h2>🏭 공급업체 평가</h2>
            <table class="table">
                <thead>
                    <tr><th>업체명</th><th>종합점수</th><th>가격경쟁력</th><th>품질신뢰도</th><th>납기준수율</th><th>평가</th></tr>
                </thead>
                <tbody>
                    {supplier_rows}
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <h2>⚠️ 리스크 분석</h2>
            <div class="info-grid">
                <div class="info-card">
                    <h4>예산 리스크</h4>
                    <div class="risk-meter risk-{budget_risk_level}"></div>
                    <p>{budget_risk_desc}</p>
                </div>
                <div class="info-card">
                    <h4>공급 리스크</h4>
                    <div class="risk-meter risk-{supply_risk_level}"></div>
                    <p>{supply_risk_desc}</p>
                </div>
                <div class="info-card">
                    <h4>품질 리스크</h4>
                    <div class="risk-meter risk-{quality_risk_level}"></div>
                    <p>{quality_risk_desc}</p>
                </div>
                <div class="info-card">
                    <h4>납기 리스크</h4>
                    <div class="risk-meter risk-{delivery_risk_level}"></div>
                    <p>{delivery_risk_desc}</p>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>💡 권고사항</h2>
            <div class="alert alert-success">
                <h4>주요 권고사항</h4>
                <ul>
                    {recommendations}
                </ul>
            </div>
        </div>
        
        <div class="footer">
            <p>본 보고서는 AI 시스템에 의해 자동 생성되었습니다.</p>
            <p>최종 의사결정 시 전문가 검토를 권장합니다.</p>
            <p>신뢰도: {confidence_score:.1%}</p>
        </div>
    </div>
</body>
</html>
        '''
        
        # 템플릿 데이터 준비
        request_data = data.get('request', {})
        market_data = data.get('market', {})
        suppliers = data.get('suppliers', [])
        risks = data.get('risks', {})
        
        # 공급업체 테이블 행 생성
        supplier_rows = ""
        for supplier in suppliers[:5]:
            score = supplier.get('overall_score', 0)
            eval_data = supplier.get('evaluation', {})
            supplier_rows += f'''
            <tr>
                <td>{supplier.get('name', 'N/A')}</td>
                <td>{score:.1f}/5.0</td>
                <td>{eval_data.get('가격 경쟁력', 0):.1f}</td>
                <td>{eval_data.get('품질 신뢰도', 0):.1f}</td>
                <td>{eval_data.get('납기 준수율', 0):.1f}</td>
                <td>{'우수' if score >= 4.0 else '보통' if score >= 3.0 else '개선필요'}</td>
            </tr>
            '''
        
        # 권고사항 리스트 생성
        research_result = data.get('research')
        recommendations = research_result.recommendations if research_result else []
        recommendations_html = "".join([f"<li>{rec}</li>" for rec in recommendations])
        
        # 가격 정보
        price_range = market_data.get('price_range', {})
        
        # 차트 생성
        price_chart = await self._generate_price_chart(market_data)
        
        # 템플릿 포맷팅
        html_content = html_template.format(
            generated_time=datetime.now().strftime("%Y년 %m월 %d일 %H:%M"),
            product_name=request_data.get('품명', 'N/A'),
            specifications=request_data.get('규격', 'N/A'),
            quantity=request_data.get('수량', 'N/A'),
            budget=request_data.get('예상단가', 'N/A'),
            total_products=market_data.get('total_products', 0),
            supplier_count=market_data.get('supplier_count', 0),
            min_price=price_range.get('min', 0),
            avg_price=price_range.get('avg', 0),
            max_price=price_range.get('max', 0),
            recommended_price=price_range.get('recommended', 0),
            price_chart=price_chart,
            supplier_rows=supplier_rows,
            budget_risk_level=self._get_risk_level_class(risks.get('budget_risk', {}).get('level', 0)),
            budget_risk_desc=risks.get('budget_risk', {}).get('description', '평가 중'),
            supply_risk_level=self._get_risk_level_class(risks.get('supply_risk', {}).get('level', 0)),
            supply_risk_desc=risks.get('supply_risk', {}).get('description', '평가 중'),
            quality_risk_level=self._get_risk_level_class(risks.get('quality_risk', {}).get('level', 0)),
            quality_risk_desc=risks.get('quality_risk', {}).get('description', '평가 중'),
            delivery_risk_level=self._get_risk_level_class(risks.get('delivery_risk', {}).get('level', 0)),
            delivery_risk_desc=risks.get('delivery_risk', {}).get('description', '평가 중'),
            recommendations=recommendations_html,
            confidence_score=research_result.confidence_score if research_result else 0.8
        )
        
        return html_content
    
    async def _generate_charts(self, data: Dict) -> Dict[str, str]:
        """차트 생성"""
        charts = {}
        
        # 가격 비교 차트
        price_chart = await self._generate_price_chart(data.get('market', {}))
        charts['price_comparison'] = price_chart
        
        # 공급업체 평가 차트
        supplier_chart = await self._generate_supplier_chart(data.get('suppliers', []))
        charts['supplier_evaluation'] = supplier_chart
        
        # 리스크 분석 차트
        risk_chart = await self._generate_risk_chart(data.get('risks', {}))
        charts['risk_analysis'] = risk_chart
        
        return charts
    
    async def _generate_price_chart(self, market_data: Dict) -> str:
        """가격 차트 생성"""
        try:
            plt.figure(figsize=(10, 6))
            
            # 샘플 데이터 (실제로는 market_data에서 추출)
            categories = ['최저가', '평균가', '최고가', '권장가']
            price_range = market_data.get('price_range', {})
            prices = [
                price_range.get('min', 100000),
                price_range.get('avg', 200000),
                price_range.get('max', 300000),
                price_range.get('recommended', 180000)
            ]
            
            colors = ['#28a745', '#007bff', '#dc3545', '#ffc107']
            bars = plt.bar(categories, prices, color=colors)
            
            plt.title('시장 가격 분석', fontsize=16, fontweight='bold')
            plt.ylabel('가격 (원)')
            plt.grid(axis='y', alpha=0.3)
            
            # 막대 위에 값 표시
            for bar, price in zip(bars, prices):
                plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(prices)*0.01,
                        f'{price:,}원', ha='center', va='bottom')
            
            plt.tight_layout()
            
            # 이미지를 base64로 인코딩
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            chart_data = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return chart_data
            
        except Exception as e:
            logger.warning(f"가격 차트 생성 실패: {e}")
            return ""
    
    async def _generate_supplier_chart(self, suppliers: List[Dict]) -> str:
        """공급업체 평가 차트 생성"""
        try:
            if not suppliers:
                return ""
            
            plt.figure(figsize=(12, 8))
            
            # 상위 5개 공급업체
            top_suppliers = suppliers[:5]
            names = [s.get('name', f'업체{i+1}') for i, s in enumerate(top_suppliers)]
            scores = [s.get('overall_score', 0) for s in top_suppliers]
            
            colors = plt.cm.RdYlGn([score/5.0 for score in scores])
            bars = plt.barh(names, scores, color=colors)
            
            plt.title('공급업체 종합 평가', fontsize=16, fontweight='bold')
            plt.xlabel('종합 점수')
            plt.xlim(0, 5)
            plt.grid(axis='x', alpha=0.3)
            
            # 점수 표시
            for bar, score in zip(bars, scores):
                plt.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height()/2,
                        f'{score:.1f}', va='center')
            
            plt.tight_layout()
            
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            chart_data = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return chart_data
            
        except Exception as e:
            logger.warning(f"공급업체 차트 생성 실패: {e}")
            return ""
    
    async def _generate_risk_chart(self, risks: Dict) -> str:
        """리스크 차트 생성"""
        try:
            if not risks:
                return ""
            
            plt.figure(figsize=(10, 8))
            
            risk_categories = ['예산', '공급', '품질', '납기', '시장']
            risk_levels = []
            
            for category in ['budget_risk', 'supply_risk', 'quality_risk', 'delivery_risk', 'market_risk']:
                level = risks.get(category, {}).get('level', 0)
                risk_levels.append(level)
            
            # 레이더 차트
            angles = [i * 2 * 3.14159 / len(risk_categories) for i in range(len(risk_categories))]
            angles += angles[:1]  # 원형으로 만들기
            risk_levels += risk_levels[:1]
            
            ax = plt.subplot(111, projection='polar')
            ax.plot(angles, risk_levels, 'o-', linewidth=2, color='#dc3545')
            ax.fill(angles, risk_levels, alpha=0.25, color='#dc3545')
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(risk_categories)
            ax.set_ylim(0, 5)
            ax.set_title('리스크 분석', size=16, fontweight='bold', pad=20)
            ax.grid(True)
            
            plt.tight_layout()
            
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            chart_data = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return chart_data
            
        except Exception as e:
            logger.warning(f"리스크 차트 생성 실패: {e}")
            return ""
    
    # 헬퍼 메서드들
    def _calculate_price_range(self, products: List[Dict]) -> Dict[str, int]:
        """가격 범위 계산"""
        if not products:
            return {'min': 0, 'max': 0, 'avg': 0, 'recommended': 0}
        
        prices = []
        for product in products:
            price = product.get('price', 0)
            if isinstance(price, (int, float)) and price > 0:
                prices.append(price)
        
        if not prices:
            return {'min': 0, 'max': 0, 'avg': 0, 'recommended': 0}
        
        min_price = min(prices)
        max_price = max(prices)
        avg_price = sum(prices) // len(prices)
        recommended_price = int(avg_price * 0.9)  # 평균의 90%
        
        return {
            'min': min_price,
            'max': max_price,
            'avg': avg_price,
            'recommended': recommended_price
        }
    
    def _determine_market_trend(self, products: List[Dict]) -> str:
        """시장 동향 판단"""
        if len(products) > 50:
            return "활발한 시장"
        elif len(products) > 20:
            return "안정적 시장"
        else:
            return "제한적 시장"
    
    def _assess_competition_level(self, products: List[Dict]) -> str:
        """경쟁 수준 평가"""
        unique_suppliers = len(set([p.get('supplier', '') for p in products]))
        if unique_suppliers > 20:
            return "높음"
        elif unique_suppliers > 10:
            return "보통"
        else:
            return "낮음"
    
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
        # 납기일 정보가 있다면 분석 (현재는 기본값)
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
    
    def _get_risk_level_class(self, level: float) -> str:
        """리스크 레벨 CSS 클래스"""
        if level <= 2:
            return "low"
        elif level <= 3:
            return "medium"
        else:
            return "high"
    
    async def _analyze_market_trends(self, request_data: Dict) -> Dict[str, Any]:
        """시장 동향 분석"""
        # RAG를 통한 시장 동향 분석
        trend_query = f"{request_data.get('품명', '')} 시장 동향 트렌드 전망"
        trends = await self.rag_module.advanced_search_with_context(
            query=trend_query,
            max_results=5
        )
        
        return trends.get('market_trends', {})
    
    async def _analyze_price_trends(self, request_data: Dict) -> List[Dict]:
        """가격 동향 분석"""
        # 가격 히스토리 분석 (실제로는 더 복잡한 로직 필요)
        price_trends = []
        
        for i in range(12):  # 12개월 데이터
            date = datetime.now() - timedelta(days=30*i)
            # 실제로는 데이터베이스에서 가격 데이터를 가져와야 함
            price_trends.append({
                'date': date.strftime('%Y-%m'),
                'price': 200000 + (i * 5000),  # 샘플 데이터
                'change_rate': round((i * 0.5), 1)
            })
        
        return price_trends
    
    async def _generate_executive_summary(self, data: Dict) -> str:
        """경영진 요약 보고서 생성"""
        request_data = data.get('request', {})
        market_data = data.get('market', {})
        risks = data.get('risks', {})
        
        summary = f"""
# 경영진 요약 보고서

## 조달 개요
- **품목**: {request_data.get('품명', 'N/A')}
- **예상 예산**: {request_data.get('예상단가', 'N/A')}
- **수량**: {request_data.get('수량', 'N/A')}

## 핵심 분석 결과
- **시장 규모**: {market_data.get('total_products', 0)}개 제품 확인
- **가격 경쟁력**: 시장 평균 대비 {self._calculate_price_competitiveness(request_data, market_data)}
- **공급업체 현황**: {market_data.get('supplier_count', 0)}개 업체 확인

## 주요 리스크
- **전체 리스크 레벨**: {risks.get('overall', {}).get('category', '평가 중')}
- **핵심 관심사항**: {self._get_key_concerns(risks)}

## 권고 결정
- **조달 추천도**: {'권장' if risks.get('overall', {}).get('level', 3) <= 2 else '신중 검토'}
- **예상 절감 효과**: {self._calculate_savings_potential(request_data, market_data)}

본 분석은 AI 시스템 기반으로 생성되었으며, 최종 의사결정 시 전문가 검토를 권장합니다.
        """
        
        return summary.strip()
    
    async def _generate_detailed_analysis(self, data: Dict) -> str:
        """상세 분석 보고서 생성"""
        # LLM을 통한 상세 분석 생성
        if self.llm_module and self.llm_module.check_server_health():
            analysis_prompt = f"""
다음 조달 데이터를 기반으로 상세한 분석 보고서를 작성해주세요:

요청 정보: {json.dumps(data.get('request', {}), ensure_ascii=False)}
시장 데이터: {json.dumps(data.get('market', {}), ensure_ascii=False)}
리스크 분석: {json.dumps(data.get('risks', {}), ensure_ascii=False)}

다음 관점에서 분석해주세요:
1. 시장 포지셔닝 분석
2. 경쟁 우위 요소
3. 조달 최적화 방안
4. 향후 시장 전망
5. 구체적 실행 계획

전문적이고 실용적인 분석을 제공해주세요.
            """
            
            try:
                detailed_analysis = self.llm_module.generate_completion(analysis_prompt, max_tokens=1000)
                return detailed_analysis
            except Exception as e:
                logger.warning(f"LLM 상세 분석 생성 실패: {e}")
        
        # 기본 상세 분석
        return """
# 상세 분석 보고서

## 시장 분석
현재 시장 상황을 종합적으로 분석한 결과, 안정적인 조달 환경이 조성되어 있습니다.

## 공급업체 분석
다양한 공급업체가 경쟁하고 있어 선택의 폭이 넓습니다.

## 리스크 관리
주요 리스크 요인들이 식별되었으며, 적절한 관리 방안이 필요합니다.

## 권고사항
전문가 검토를 통한 최종 의사결정을 권장합니다.
        """
    
    def _calculate_price_competitiveness(self, request_data: Dict, market_data: Dict) -> str:
        """가격 경쟁력 계산"""
        try:
            requested_budget = int(str(request_data.get('예상단가', '0')).replace(',', '').replace('원', ''))
            market_avg = market_data.get('price_range', {}).get('avg', 0)
            
            if requested_budget == 0 or market_avg == 0:
                return "평가 불가"
            
            ratio = requested_budget / market_avg
            
            if ratio >= 1.1:
                return "높음 (시장 평균 대비 +10% 이상)"
            elif ratio >= 0.9:
                return "적정 (시장 평균 수준)"
            else:
                return "낮음 (시장 평균 대비 -10% 이하)"
                
        except Exception:
            return "평가 불가"
    
    def _get_key_concerns(self, risks: Dict) -> str:
        """주요 관심사항 추출"""
        high_risks = []
        for risk_type, risk_data in risks.items():
            if risk_type == 'overall':
                continue
            if risk_data.get('level', 0) >= 3:
                high_risks.append(risk_type.replace('_risk', '').replace('_', ' ').title())
        
        return ", ".join(high_risks) if high_risks else "없음"
    
    def _calculate_savings_potential(self, request_data: Dict, market_data: Dict) -> str:
        """절감 잠재력 계산"""
        try:
            requested_budget = int(str(request_data.get('예상단가', '0')).replace(',', '').replace('원', ''))
            recommended_price = market_data.get('price_range', {}).get('recommended', 0)
            
            if requested_budget == 0 or recommended_price == 0:
                return "산출 불가"
            
            savings = requested_budget - recommended_price
            if savings > 0:
                percentage = (savings / requested_budget) * 100
                return f"{savings:,}원 ({percentage:.1f}% 절감 가능)"
            else:
                return "절감 효과 제한적"
                
        except Exception:
            return "산출 불가"

# 디버그 및 테스트
if __name__ == "__main__":
    async def test_enhanced_generator():
        generator = EnhancedDocumentGenerator()
        
        test_request = {
            '품명': 'GPU 그래픽카드',
            '규격': 'RTX 4070, 12GB VRAM',
            '수량': '3개',
            '예상단가': '1,500,000원',
            '사용용도': 'AI 머신러닝 작업용'
        }
        
        try:
            document = await generator.generate_comprehensive_procurement_document(test_request)
            
            print("=== 종합 조달 문서 생성 완료 ===")
            print(f"신뢰도: {document['metadata']['confidence_score']:.1%}")
            print(f"생성 시각: {document['metadata']['generated_at']}")
            print("\n=== 경영진 요약 ===")
            print(document['executive_summary'])
            
        except Exception as e:
            logger.error(f"테스트 실패: {e}")
    
    asyncio.run(test_enhanced_generator())
