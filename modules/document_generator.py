#!/usr/bin/env python3
"""
LLM 기반 자동 문서화 시스템
조달 정보를 구조화된 문서로 자동 변환
"""

import asyncio
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass
from utils import get_logger, prompt_loader

logger = get_logger(__name__)

@dataclass
class ProcurementRequirement:
    """조달 요구사항 데이터 클래스"""
    id: str
    category: str
    budget_min: float
    budget_max: float
    delivery_days: int
    specifications: Dict[str, Any]
    priority_weights: Dict[str, float]
    organization: str = ""
    urgency: str = "보통"
    description: str = ""

class ProcurementDocumentGenerator:
    """조달 문서 자동 생성기"""
    
    def __init__(self):
        # 순환 import 방지를 위해 동적 import
        try:
            from modules.llm_module import LlmModule
            self.llm_module = LlmModule()
        except Exception as e:
            logger.warning(f"LLM 모듈 로드 실패: {e}")
            self.llm_module = None

    
    async def generate_product_analysis_report(
        self, 
        product: Any,  # UnifiedProduct 타입
        requirement: ProcurementRequirement,
        matching_scores: Dict[str, float]
    ) -> str:
        """제품 분석 보고서 생성"""
        logger.info(f"제품 분석 보고서 생성: {product.name['normalized']}")
        
        # 데이터 포맷팅
        product_data = self._format_product_data(product)
        requirement_data = self._format_requirement_data(requirement)
        matching_data = self._format_matching_scores(matching_scores)
        
        # 프롬프트 생성
        prompt = prompt_loader.get_prompt("document_generation_prompts", "product_analysis").format(
            product_data=product_data,
            requirement_data=requirement_data,
            matching_scores=matching_data
        )
        
        # LLM을 통한 보고서 생성
        report = await self._generate_with_llm(prompt)
        
        # 후처리 및 검증
        validated_report = self._validate_and_enhance_report(report, "product_analysis")
        
        logger.info("제품 분석 보고서 생성 완료")
        return validated_report
            
    
    async def generate_comparison_report(
        self, 
        products: List[Any],  # List[UnifiedProduct] 타입
        requirement: ProcurementRequirement,
        analysis_results: List[Dict]
    ) -> str:
        """제품 비교 보고서 생성"""
        logger.info(f"제품 비교 보고서 생성: {len(products)}개 제품")
        
        # 데이터 포맷팅
        products_data = self._format_products_comparison_data(products, analysis_results)
        requirement_data = self._format_requirement_data(requirement)
        
        # 프롬프트 생성
        prompt = prompt_loader.get_prompt("document_generation_prompts", "comparison_report").format(
            products_data=products_data,
            requirement_data=requirement_data
        )
        
        # LLM을 통한 보고서 생성
        report = await self._generate_with_llm(prompt)
        
        # 후처리 및 검증
        validated_report = self._validate_and_enhance_report(report, "comparison_report")
        
        logger.info("제품 비교 보고서 생성 완료")
        return validated_report

    
    async def generate_procurement_specification(
        self, 
        request_info: Dict, 
        reference_products: List[Any]  # List[UnifiedProduct] 타입
    ) -> str:
        """조달 사양서 생성"""
        logger.info("조달 사양서 생성")
        
        # 데이터 포맷팅
        request_data = self._format_request_info(request_info)
        products_data = self._format_reference_products_data(reference_products)
        
        # 프롬프트 생성
        prompt = prompt_loader.get_prompt("document_generation_prompts", "procurement_specification").format(
            request_info=request_data,
            reference_products=products_data
        )
        
        # LLM을 통한 사양서 생성
        specification = await self._generate_with_llm(prompt)
        
        # 후처리 및 검증
        validated_spec = self._validate_and_enhance_report(specification, "procurement_specification")
        
        logger.info("조달 사양서 생성 완료")
        return validated_spec

    
    async def generate_risk_assessment(
        self, 
        procurement_plan: Dict, 
        market_analysis: Dict
    ) -> str:
        """리스크 평가 보고서 생성"""
        logger.info("리스크 평가 보고서 생성")
        
        # 데이터 포맷팅
        plan_data = self._format_procurement_plan(procurement_plan)
        market_data = self._format_market_analysis(market_analysis)
        
        # 프롬프트 생성
        prompt = prompt_loader.get_prompt("document_generation_prompts", "risk_assessment").format(
            procurement_plan=plan_data,
            market_analysis=market_data
        )
        
        # LLM을 통한 평가서 생성
        assessment = await self._generate_with_llm(prompt)
        
        # 후처리 및 검증
        validated_assessment = self._validate_and_enhance_report(assessment, "risk_assessment")
        
        logger.info("리스크 평가 보고서 생성 완료")
        return validated_assessment

    
    async def _generate_with_llm(self, prompt: str) -> str:
        """LLM을 통한 텍스트 생성"""
        # LLM 모듈이 정상적으로 작동하는지 확인
        if not self.llm_module.check_server_health():
            logger.warning("LLM 서버 연결 실패 - 기본 템플릿 사용")
            return self._generate_basic_template()
        
        # 조달 요청 분석 함수를 활용하여 문서 생성
        # 실제로는 별도의 문서 생성 API가 필요하지만, 기존 함수를 활용
        analysis_result = self.llm_module.analyze_procurement_request(prompt)
        
        # 분석 결과를 문서 형태로 변환
        if isinstance(analysis_result, dict):
            return self._convert_analysis_to_document(analysis_result)
        else:
            return str(analysis_result)

    def _format_product_data(self, product: Any) -> str:  # UnifiedProduct 타입
        """제품 데이터 포맷팅"""
        lines = [
            f"제품명: {product.name['normalized']}",
            f"카테고리: {' > '.join(product.category)}",
            f"가격: {product.price['amount']:,}원",
            f"공급처: {product.source.upper()}"
        ]
        
        # 주요 사양 추가
        if product.specifications:
            lines.append("\n주요 사양:")
            for key, value in list(product.specifications.items())[:10]:
                if value and str(value).strip():
                    lines.append(f"- {key}: {value}")
        
        # 메타데이터 추가
        if product.metadata:
            lines.append("\n추가 정보:")
            for key, value in product.metadata.items():
                if value and str(value).strip():
                    lines.append(f"- {key}: {value}")
        
        return "\n".join(lines)
    
    def _format_requirement_data(self, requirement: ProcurementRequirement) -> str:
        """요구사항 데이터 포맷팅"""
        lines = [
            f"조달 카테고리: {requirement.category}",
            f"예산 범위: {requirement.budget_min:,}원 ~ {requirement.budget_max:,}원",
            f"납기: {requirement.delivery_days}일 이내",
            f"긴급도: {requirement.urgency}"
        ]
        
        if requirement.organization:
            lines.append(f"요청 기관: {requirement.organization}")
        
        if requirement.description:
            lines.append(f"상세 요구사항: {requirement.description}")
        
        if requirement.specifications:
            lines.append("\n필수 사양:")
            for key, value in requirement.specifications.items():
                lines.append(f"- {key}: {value}")
        
        if requirement.priority_weights:
            lines.append("\n우선순위 가중치:")
            for key, weight in requirement.priority_weights.items():
                lines.append(f"- {key}: {weight:.1f}")
        
        return "\n".join(lines)
    
    def _format_matching_scores(self, scores: Dict[str, float]) -> str:
        """매칭 점수 포맷팅"""
        if not scores:
            return "매칭 점수 정보 없음"
        
        lines = []
        for category, score in scores.items():
            percentage = score * 100
            lines.append(f"- {category}: {percentage:.1f}%")
        
        return "\n".join(lines)
    
    def _format_products_comparison_data(self, products: List[Any], results: List[Dict]) -> str:  # List[UnifiedProduct] 타입
        """제품 비교 데이터 포맷팅"""
        lines = []
        
        for i, product in enumerate(products):
            lines.append(f"\n=== 제품 {i+1}: {product.name['normalized']} ===")
            lines.append(f"가격: {product.price['amount']:,}원")
            lines.append(f"공급처: {product.source.upper()}")
            lines.append(f"카테고리: {' > '.join(product.category)}")
            
            # 분석 결과가 있으면 추가
            if i < len(results) and results[i]:
                result = results[i]
                if 'score' in result:
                    lines.append(f"종합 점수: {result['score']:.2f}")
                if 'match_details' in result:
                    details = result['match_details']
                    for key, value in details.items():
                        lines.append(f"- {key}: {value}")
        
        return "\n".join(lines)
    
    def _format_request_info(self, request_info: Dict) -> str:
        """요청 정보 포맷팅"""
        lines = []
        for key, value in request_info.items():
            if value:
                lines.append(f"{key}: {value}")
        return "\n".join(lines)
    
    def _format_reference_products_data(self, products: List[Any]) -> str:  # List[UnifiedProduct] 타입
        """참고 제품 데이터 포맷팅"""
        lines = []
        for i, product in enumerate(products[:5]):  # 최대 5개만
            lines.append(f"참고 제품 {i+1}: {product.name['normalized']}")
            lines.append(f"- 가격: {product.price['amount']:,}원")
            lines.append(f"- 사양: {json.dumps(product.specifications, ensure_ascii=False)}")
        return "\n".join(lines)
    
    def _format_procurement_plan(self, plan: Dict) -> str:
        """조달 계획 포맷팅"""
        return json.dumps(plan, ensure_ascii=False, indent=2)
    
    def _format_market_analysis(self, analysis: Dict) -> str:
        """시장 분석 포맷팅"""
        return json.dumps(analysis, ensure_ascii=False, indent=2)
    
    def _validate_and_enhance_report(self, report: str, report_type: str) -> str:
        """보고서 검증 및 개선"""
        if not report or len(report.strip()) < 100:
            logger.warning(f"생성된 보고서가 너무 짧음: {len(report)}")
            return self._generate_fallback_report(report_type)
        
        # 기본적인 후처리
        enhanced_report = report.strip()
        
        # 보고서 헤더 추가
        timestamp = datetime.now().strftime("%Y년 %m월 %d일 %H:%M")
        header = f"# 조달 분석 보고서\n\n**생성일시:** {timestamp}\n**보고서 유형:** {report_type}\n\n---\n\n"
        
        enhanced_report = header + enhanced_report
        
        # 보고서 푸터 추가
        footer = f"\n\n---\n\n*본 보고서는 AI 시스템에 의해 자동 생성되었습니다.*\n*최종 의사결정 시 전문가 검토를 권장합니다.*"
        enhanced_report += footer
        
        return enhanced_report
    
    def _convert_analysis_to_document(self, analysis: Dict) -> str:
        """분석 결과를 문서로 변환"""
        lines = [
            "# 조달 요청 분석 결과",
            "",
            "## 추출된 정보"
        ]
        
        if analysis.get('items'):
            lines.extend([
                "",
                "### 조달 품목",
                ""
            ])
            for item in analysis['items']:
                lines.append(f"- {item}")
        
        if analysis.get('quantities'):
            lines.extend([
                "",
                "### 수량 정보",
                ""
            ])
            for qty in analysis['quantities']:
                lines.append(f"- {qty}")
        
        if analysis.get('budget_range'):
            lines.extend([
                "",
                f"### 예산 범위: {analysis['budget_range']}",
                ""
            ])
        
        if analysis.get('urgency'):
            lines.extend([
                "",
                f"### 긴급도: {analysis['urgency']}",
                ""
            ])
        
        if analysis.get('specifications'):
            lines.extend([
                "",
                "### 상세 요구사항",
                ""
            ])
            for spec in analysis['specifications']:
                lines.append(f"- {spec}")
        
        return "\n".join(lines)
    
    def _generate_basic_template(self) -> str:
        """기본 템플릿 생성"""
        return """
# 조달 분석 보고서

## 1. 개요
조달 요청에 대한 기본 분석을 수행했습니다.

## 2. 분석 결과
상세한 분석을 위해서는 LLM 서버 연결이 필요합니다.

## 3. 권고사항
- 전문가 검토 필요
- 추가 정보 수집 권장
        """.strip()
    
    def _generate_fallback_product_report(self, product: Any, requirement: ProcurementRequirement) -> str:  # UnifiedProduct 타입
        """기본 제품 보고서 생성"""
        return f"""
# 제품 분석 보고서

## 제품 개요
- **제품명:** {product.name['normalized']}
- **가격:** {product.price['amount']:,}원
- **카테고리:** {' > '.join(product.category)}
- **공급처:** {product.source.upper()}

## 요구사항 대비 분석
- **예산 적합성:** {'적합' if requirement.budget_min <= float(product.price['amount']) <= requirement.budget_max else '부적합'}
- **카테고리 일치:** {'일치' if requirement.category in product.category else '불일치'}

## 권고사항
- 상세한 분석을 위해 전문가 검토가 필요합니다.
- 추가 제품 정보 수집을 권장합니다.
        """.strip()
    
    def _generate_fallback_comparison_report(self, products: List[Any], requirement: ProcurementRequirement) -> str:  # List[UnifiedProduct] 타입
        """기본 비교 보고서 생성"""
        lines = [
            "# 제품 비교 보고서",
            "",
            "## 비교 대상 제품"
        ]
        
        for i, product in enumerate(products):
            lines.extend([
                f"",
                f"### 제품 {i+1}: {product.name['normalized']}",
                f"- 가격: {product.price['amount']:,}원",
                f"- 공급처: {product.source.upper()}",
                f"- 카테고리: {' > '.join(product.category)}"
            ])
        
        lines.extend([
            "",
            "## 권고사항",
            "- 상세한 비교 분석을 위해 전문가 검토가 필요합니다.",
            "- 각 제품의 세부 사양을 추가로 확인하시기 바랍니다."
        ])
        
        return "\n".join(lines)
    
    def _generate_fallback_specification(self, request_info: Dict) -> str:
        """기본 사양서 생성"""
        return f"""
# 조달 사양서

## 조달 개요
{json.dumps(request_info, ensure_ascii=False, indent=2)}

## 기본 요구사항
- 상세 사양은 전문가와 협의하여 결정
- 품질 기준 및 인증 요구사항 확인 필요
- 납품 및 검수 조건 별도 협의

## 주의사항
본 사양서는 기본 템플릿입니다. 실제 조달 시에는 전문가 검토를 받으시기 바랍니다.
        """.strip()
    
    def _generate_fallback_risk_assessment(self, plan: Dict) -> str:
        """기본 리스크 평가 생성"""
        return f"""
# 리스크 평가 보고서

## 조달 계획 개요
{json.dumps(plan, ensure_ascii=False, indent=2)}

## 일반적인 조달 리스크
- **예산 리스크:** 예산 초과 가능성
- **납기 리스크:** 배송 지연 위험
- **품질 리스크:** 사양 미충족 가능성
- **공급업체 리스크:** 업체 신뢰도 이슈

## 권고사항
- 상세한 리스크 분석을 위해 전문가 검토 필요
- 시장 조사 및 업체 평가 수행 권장
        """.strip()
    
    def _generate_fallback_report(self, report_type: str) -> str:
        """기본 대체 보고서 생성"""
        templates = {
            "product_analysis": self._generate_basic_template(),
            "comparison_report": "# 제품 비교 보고서\n\n상세한 비교를 위해 전문가 검토가 필요합니다.",
            "procurement_specification": "# 조달 사양서\n\n전문가와 협의하여 상세 사양을 결정해주세요.",
            "risk_assessment": "# 리스크 평가\n\n전문가 리스크 분석이 필요합니다."
        }
        
        return templates.get(report_type, self._generate_basic_template())

# 사용 예시
async def test_document_generator():
    """문서 생성기 테스트"""
    generator = ProcurementDocumentGenerator()
    
    # 테스트 데이터 - 동적 import
    from modules.data_processor import UnifiedProduct
    from decimal import Decimal
    
    test_product = UnifiedProduct(
        id="test_doc_1",
        source="coupang",
        name={
            "original": "사무용 책상 1800x800",
            "normalized": "사무용 책상",
            "searchable": "사무용 책상"
        },
        price={
            "amount": Decimal("450000"),
            "currency": "KRW",
            "vat_included": True
        },
        category=["사무용품", "가구"],
        specifications={"크기": "1800x800mm", "재질": "MDF"},
        metadata={"vendor": "테스트 업체"},
        timestamps={"created": datetime.now()}
    )
    
    test_requirement = ProcurementRequirement(
        id="req_1",
        category="사무용품",
        budget_min=300000,
        budget_max=600000,
        delivery_days=14,
        specifications={"크기": "1800x800mm 이상"},
        priority_weights={"price": 0.4, "quality": 0.6},
        organization="테스트 기관"
    )
    
    # 제품 분석 보고서 생성
    matching_scores = {"price": 0.8, "specifications": 0.9, "delivery": 0.7}
    report = await generator.generate_product_analysis_report(
        test_product, 
        test_requirement, 
        matching_scores
    )
    
    print("=== 제품 분석 보고서 ===")
    print(report)
    print("\n" + "="*50 + "\n")
    
    # 조달 사양서 생성
    request_info = {
        "품목": "사무용 책상",
        "수량": "10개",
        "예산": "500만원",
        "납기": "2주"
    }
    
    spec = await generator.generate_procurement_specification(
        request_info, 
        [test_product]
    )
    
    print("=== 조달 사양서 ===")
    print(spec)

if __name__ == "__main__":
    asyncio.run(test_document_generator())
