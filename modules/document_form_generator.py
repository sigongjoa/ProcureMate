#!/usr/bin/env python3
"""
한국 기업 구매-조달 문서 생성기
9가지 핵심 문서의 동적 폼 생성 및 문서 자동화
"""

import json
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from pathlib import Path
from modules.llm_module import LlmModule
from utils import get_logger, prompt_loader

logger = get_logger(__name__)

@dataclass
class DocumentFormField:
    """문서 폼 필드 정의"""
    name: str
    label: str
    field_type: str  # text, number, date, select, textarea, checkbox
    required: bool = True
    options: List[str] = None
    placeholder: str = ""
    validation: str = ""

@dataclass
class DocumentTemplate:
    """문서 템플릿 정의"""
    id: str
    name: str
    description: str
    category: str
    fields: List[DocumentFormField]
    output_formats: List[str]  # pdf, xlsx, docx, xml, etc

class DocumentFormGenerator:
    """문서 폼 생성 및 관리 클래스"""
    
    def __init__(self):
        self.llm_module = LlmModule()
        self.templates = self._initialize_templates()
        
    def _initialize_templates(self) -> Dict[str, DocumentTemplate]:
        """9가지 핵심 문서 템플릿 초기화"""
        templates = {}
        
        # 1. 구매요청서(PR)
        templates["purchase_request"] = DocumentTemplate(
            id="purchase_request",
            name="구매요청서(PR)",
            description="내부 구매 요청을 위한 기본 문서",
            category="구매관리",
            fields=[
                DocumentFormField("RequesterName", "요청자명", "text"),
                DocumentFormField("Department", "부서", "text"),
                DocumentFormField("ContactInfo", "연락처", "text"),
                DocumentFormField("ItemName", "품명", "text"),
                DocumentFormField("Specification", "규격", "textarea"),
                DocumentFormField("Quantity", "수량", "number"),
                DocumentFormField("EstimatedPrice", "예상단가", "number"),
                DocumentFormField("Purpose", "사용용도", "textarea"),
                DocumentFormField("Urgency", "긴급도", "select", options=["HIGH", "MEDIUM", "LOW"]),
                DocumentFormField("DeliveryDate", "희망납기일", "date"),
                DocumentFormField("DeliveryLocation", "납품장소", "text"),
                DocumentFormField("BudgetCode", "예산과목", "text"),
                DocumentFormField("ApprovedBudget", "승인예산액", "number")
            ],
            output_formats=["pdf", "xlsx", "docx"]
        )
        
        # 2. 견적 비교표
        templates["quote_comparison"] = DocumentTemplate(
            id="quote_comparison",
            name="견적 비교표",
            description="다중 업체 견적 비교 분석",
            category="구매관리",
            fields=[
                DocumentFormField("ProjectName", "프로젝트명", "text"),
                DocumentFormField("RequestDate", "요청일", "date"),
                DocumentFormField("ComparisonCriteria", "비교기준", "textarea", 
                                placeholder="가격 40%, 품질 30%, 납기 20%, 신뢰도 10%"),
                DocumentFormField("Vendor1Name", "업체1 상호", "text"),
                DocumentFormField("Vendor1Price", "업체1 단가", "number"),
                DocumentFormField("Vendor1Spec", "업체1 규격", "textarea"),
                DocumentFormField("Vendor1Delivery", "업체1 납기", "text"),
                DocumentFormField("Vendor2Name", "업체2 상호", "text"),
                DocumentFormField("Vendor2Price", "업체2 단가", "number"),
                DocumentFormField("Vendor2Spec", "업체2 규격", "textarea"),
                DocumentFormField("Vendor2Delivery", "업체2 납기", "text"),
                DocumentFormField("Vendor3Name", "업체3 상호", "text"),
                DocumentFormField("Vendor3Price", "업체3 단가", "number"),
                DocumentFormField("Vendor3Spec", "업체3 규격", "textarea"),
                DocumentFormField("Vendor3Delivery", "업체3 납기", "text")
            ],
            output_formats=["pdf", "xlsx"]
        )
        
        # 3. 구매승인서
        templates["purchase_approval"] = DocumentTemplate(
            id="purchase_approval",
            name="구매승인서",
            description="전자결재용 구매승인 문서",
            category="결재관리",
            fields=[
                DocumentFormField("PRNumber", "구매요청번호", "text"),
                DocumentFormField("ItemSummary", "구매품목", "textarea"),
                DocumentFormField("SelectedVendor", "선정업체", "text"),
                DocumentFormField("SelectionReason", "선정사유", "textarea"),
                DocumentFormField("TotalAmount", "계약금액", "number"),
                DocumentFormField("BudgetCode", "예산과목", "text"),
                DocumentFormField("RemainingBudget", "잔여예산", "number"),
                DocumentFormField("PaymentTerms", "결제조건", "text"),
                DocumentFormField("DeliveryTerms", "납기조건", "text"),
                DocumentFormField("SpecialTerms", "특별조건", "textarea", required=False)
            ],
            output_formats=["pdf", "docx"]
        )
        
        # 4. 구매주문서(PO)
        templates["purchase_order"] = DocumentTemplate(
            id="purchase_order",
            name="구매주문서(PO)",
            description="공급업체 발송용 주문서",
            category="주문관리",
            fields=[
                DocumentFormField("PONumber", "주문번호", "text"),
                DocumentFormField("OrderDate", "주문일", "date"),
                DocumentFormField("VendorName", "공급업체명", "text"),
                DocumentFormField("VendorBRN", "사업자등록번호", "text"),
                DocumentFormField("VendorAddress", "업체주소", "textarea"),
                DocumentFormField("ContactPerson", "담당자", "text"),
                DocumentFormField("ItemCode", "품목코드", "text"),
                DocumentFormField("ItemName", "품명", "text"),
                DocumentFormField("Specification", "규격", "textarea"),
                DocumentFormField("Quantity", "수량", "number"),
                DocumentFormField("UnitPrice", "단가", "number"),
                DocumentFormField("TotalAmount", "총액", "number"),
                DocumentFormField("DeliveryDate", "납기일", "date"),
                DocumentFormField("DeliveryLocation", "납품장소", "textarea"),
                DocumentFormField("PaymentTerms", "결제조건", "text")
            ],
            output_formats=["pdf", "csv"]
        )
        
        # 5. 검수조서
        templates["inspection_report"] = DocumentTemplate(
            id="inspection_report",
            name="검수조서/납품확인서",
            description="품질검사 및 납품확인 문서",
            category="검수관리",
            fields=[
                DocumentFormField("InspectionID", "검수번호", "text"),
                DocumentFormField("PONumber", "주문번호", "text"),
                DocumentFormField("InspectionDate", "검수일", "date"),
                DocumentFormField("Inspector", "검수자", "text"),
                DocumentFormField("ItemName", "품명", "text"),
                DocumentFormField("OrderedQty", "주문수량", "number"),
                DocumentFormField("DeliveredQty", "납품수량", "number"),
                DocumentFormField("PassedQty", "합격수량", "number"),
                DocumentFormField("FailedQty", "불합격수량", "number"),
                DocumentFormField("QualityStandard", "품질기준", "textarea"),
                DocumentFormField("InspectionResult", "검수결과", "select", 
                                options=["합격", "불합격", "조건부합격"]),
                DocumentFormField("DefectDetails", "불량내용", "textarea", required=False),
                DocumentFormField("ActionRequired", "조치사항", "textarea", required=False)
            ],
            output_formats=["pdf"]
        )
        
        # 6. 세금계산서
        templates["tax_invoice"] = DocumentTemplate(
            id="tax_invoice",
            name="세금계산서/지급통의서",
            description="국세청 호환 전자세금계산서",
            category="세무관리",
            fields=[
                DocumentFormField("InvoiceNumber", "계산서번호", "text"),
                DocumentFormField("IssueDate", "발행일", "date"),
                DocumentFormField("SupplierName", "공급자상호", "text"),
                DocumentFormField("SupplierBRN", "공급자사업자번호", "text"),
                DocumentFormField("SupplierAddress", "공급자주소", "textarea"),
                DocumentFormField("BuyerName", "공급받는자상호", "text"),
                DocumentFormField("BuyerBRN", "공급받는자사업자번호", "text"),
                DocumentFormField("ItemName", "품명", "text"),
                DocumentFormField("Quantity", "수량", "number"),
                DocumentFormField("UnitPrice", "단가", "number"),
                DocumentFormField("SupplyAmount", "공급가액", "number"),
                DocumentFormField("TaxAmount", "세액", "number"),
                DocumentFormField("TotalAmount", "합계", "number"),
                DocumentFormField("PaymentDueDate", "지급기한", "date")
            ],
            output_formats=["xml", "pdf"]
        )
        
        # 7. 지출결산 리포트
        templates["expense_report"] = DocumentTemplate(
            id="expense_report",
            name="지출결산 리포트",
            description="K-IFRS 기준 지출 분석 보고서",
            category="회계관리",
            fields=[
                DocumentFormField("ReportPeriod", "보고기간", "text", placeholder="2024년 1분기"),
                DocumentFormField("PersonnelCost", "인건비", "number"),
                DocumentFormField("OutsourcingCost", "외주비", "number"),
                DocumentFormField("OperatingCost", "운영비", "number"),
                DocumentFormField("TaxesCost", "세금과공과", "number"),
                DocumentFormField("OtherCost", "기타비용", "number"),
                DocumentFormField("TotalBudget", "총예산", "number"),
                DocumentFormField("HeadCount", "인원수", "number"),
                DocumentFormField("Department", "부서", "text"),
                DocumentFormField("PreviousAmount", "전년동기", "number", required=False),
                DocumentFormField("KPITargets", "KPI목표", "textarea", required=False)
            ],
            output_formats=["xlsx", "pdf"]
        )
        
        return templates
    
    def get_document_types(self) -> List[Dict[str, str]]:
        """사용 가능한 문서 타입 목록 반환"""
        return [
            {
                "id": template.id,
                "name": template.name,
                "description": template.description,
                "category": template.category
            }
            for template in self.templates.values()
        ]
    
    def get_form_fields(self, document_type: str) -> List[Dict[str, Any]]:
        """특정 문서 타입의 폼 필드 정보 반환"""
        if document_type not in self.templates:
            logger.error(f"알 수 없는 문서 타입: {document_type}")
            return []
        
        template = self.templates[document_type]
        return [asdict(field) for field in template.fields]
    
    async def generate_document(self, document_type: str, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """폼 데이터를 기반으로 문서 생성"""
        logger.info(f"문서 생성 시작: {document_type}")
        
        if document_type not in self.templates:
            raise ValueError(f"지원하지 않는 문서 타입: {document_type}")
        
        template = self.templates[document_type]
        
        try:
            # 프롬프트 로드 및 생성
            prompt_template = prompt_loader.get_prompt("document_form_prompts", document_type)
            prompt = prompt_template.format(**form_data)
            
            # LLM을 통한 문서 내용 생성
            generated_content = await self._generate_with_llm(prompt)
            
            # 결과 패키징
            result = {
                "document_type": document_type,
                "template_name": template.name,
                "generated_content": generated_content,
                "form_data": form_data,
                "output_formats": template.output_formats,
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            }
            
            logger.info(f"문서 생성 완료: {document_type}")
            return result
            
        except Exception as e:
            logger.error(f"문서 생성 실패: {str(e)}", exc_info=True)
            return {
                "document_type": document_type,
                "template_name": template.name,
                "error": str(e),
                "status": "error",
                "timestamp": datetime.now().isoformat()
            }
    
    async def _generate_with_llm(self, prompt: str) -> str:
        """LLM을 통한 문서 내용 생성"""
        if not self.llm_module.check_server_health():
            logger.error("LLM 서버 연결 실패")
            raise Exception("LLM 서버 연결 실패")
        
        result = self.llm_module.analyze_procurement_request(prompt)
        
        if isinstance(result, dict):
            return self._format_llm_result(result)
        else:
            return str(result)
    
    def _format_llm_result(self, result: Dict) -> str:
        """LLM 결과를 문서 형태로 포맷팅"""
        lines = ["# 생성된 문서", "", "## 처리 결과"]
        
        for key, value in result.items():
            if value:
                lines.append(f"**{key}:** {value}")
        
        return "\n".join(lines)
