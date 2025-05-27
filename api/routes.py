#!/usr/bin/env python3
"""
API 라우터 - 모든 API 엔드포인트를 관리
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List, Optional
import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

# 상위 디렉토리의 모듈들 import
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from .models import (
    LLMTestRequest,
    RAGTestRequest, 
    TestResult,
    SystemStatus,
    WorkflowRequest
)
from .handlers import (
    LLMTestHandler,
    RAGTestHandler,
    WorkflowTestHandler,
    SystemStatusHandler,
    get_g2b_handler,
    get_coupang_handler,
    get_hybrid_search_handler,
    get_doc_generation_handler
)

from utils import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api", tags=["API"])

# 핸들러 인스턴스들
llm_handler = LLMTestHandler()
rag_handler = RAGTestHandler()
workflow_handler = WorkflowTestHandler()
status_handler = SystemStatusHandler()

@router.get("/system/status", response_model=SystemStatus)
async def get_system_status():
    """시스템 상태 조회"""
    return await status_handler.get_status()

@router.post("/llm/test")
async def test_llm(request: LLMTestRequest):
    """LLM 테스트 실행"""
    return await llm_handler.run_test(request)

@router.post("/rag/test")
async def test_rag(request: RAGTestRequest):
    """RAG 검색 테스트 실행"""
    return await rag_handler.run_test(request)

@router.post("/workflow/test")
async def test_workflow(request: WorkflowRequest):
    """전체 워크플로우 테스트 실행"""
    return await workflow_handler.run_test(request)

@router.get("/test/history")
async def get_test_history(limit: int = 50, test_type: Optional[str] = None):
    """테스트 이력 조회"""
    return await status_handler.get_test_history(limit, test_type)

@router.get("/test/{test_id}")
async def get_test_detail(test_id: str):
    """특정 테스트 상세 조회"""
    return await status_handler.get_test_detail(test_id)

@router.delete("/test/{test_id}")
async def delete_test(test_id: str):
    """테스트 결과 삭제"""
    return await status_handler.delete_test(test_id)

@router.get("/analytics/performance")
async def get_performance_analytics(days: int = 7):
    """성능 분석 데이터 조회"""
    return await status_handler.get_performance_analytics(days)

@router.get("/config")
async def get_config():
    """현재 설정 조회"""
    return await status_handler.get_config()

@router.post("/config")
async def update_config(config: Dict[str, Any]):
    """설정 업데이트"""
    return await status_handler.update_config(config)

@router.post("/system/reset")
async def reset_system():
    """시스템 초기화"""
    return await status_handler.reset_system()

@router.get("/health")
async def health_check():
    """헬스 체크"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@router.get("/llm/responses")
async def get_llm_responses(limit: int = 20):
    """최근 LLM 응답들 조회"""
    from .llm_response_handler import get_llm_response_handler
    handler = get_llm_response_handler()
    return await handler.get_llm_responses(limit)

@router.get("/llm/response/{test_id}")
async def get_llm_response_detail(test_id: str):
    """특정 LLM 응답 상세 조회"""
    from .llm_response_handler import get_llm_response_handler
    handler = get_llm_response_handler()
    result = await handler.get_llm_response_detail(test_id)
    if not result:
        raise HTTPException(status_code=404, detail="테스트 결과를 찾을 수 없습니다")
    return result

# G2B API 엔드포인트
@router.post("/g2b/search")
async def search_g2b_bids(query_params: Dict[str, Any]):
    """나라장터 입찰공고 검색"""
    handler = get_g2b_handler()
    return await handler.search_bid_announcements(query_params)

@router.get("/g2b/contract/{contract_id}")
async def get_g2b_contract(contract_id: str):
    """나라장터 계약정보 조회"""
    handler = get_g2b_handler()
    return await handler.get_contract_info(contract_id)

@router.post("/g2b/contract")
async def search_g2b_contracts(query_params: Dict[str, Any]):
    """나라장터 계약정보 검색"""
    handler = get_g2b_handler()
    return await handler.search_contract_info(query_params)

@router.post("/g2b/price")
async def search_g2b_prices(query_params: Dict[str, Any]):
    """나라장터 가격정보 조회"""
    handler = get_g2b_handler()
    return await handler.search_price_info(query_params)

# 쿠팡 API 엔드포인트
@router.post("/coupang/search")
async def search_coupang_products(request: Dict[str, Any]):
    """쿠팡 상품 검색"""
    query = request.get("query", "")
    if not query:
        raise HTTPException(status_code=400, detail="검색어가 필요합니다")
    
    search_params = {
        "limit": request.get("limit", 20),
        "min_price": request.get("min_price"),
        "max_price": request.get("max_price"),
        "category": request.get("category")
    }
    
    # None 값 제거
    search_params = {k: v for k, v in search_params.items() if v is not None}
    
    handler = get_coupang_handler()
    return await handler.search_products(query, search_params)

@router.get("/coupang/product/{product_id}")
async def get_coupang_product(product_id: str):
    """쿠팡 상품 상세정보 조회"""
    handler = get_coupang_handler()
    return await handler.get_product_details(product_id)

@router.get("/coupang/categories")
async def get_coupang_categories():
    """쿠팡 카테고리 조회"""
    handler = get_coupang_handler()
    return await handler.get_categories()

# 하이브리드 검색 엔드포인트
@router.post("/search/hybrid")
async def hybrid_search(query: str, filters: Optional[Dict[str, Any]] = None):
    """하이브리드 검색 (모든 플랫폼 통합)"""
    handler = get_hybrid_search_handler()
    return await handler.search_all_platforms(query, filters)

@router.post("/analyze/matching")
async def analyze_procurement_matching(products: List[Dict], requirements: Dict):
    """조달 요구사항 매칭 분석"""
    handler = get_hybrid_search_handler()
    return await handler.analyze_procurement_match(products, requirements)

# 문서 생성 엔드포인트
@router.post("/document/report")
async def generate_procurement_report(products: List[Dict], requirements: Dict):
    """조달 보고서 자동 생성"""
    handler = get_doc_generation_handler()
    return await handler.generate_procurement_report(products, requirements)

@router.post("/document/comparison")
async def generate_comparison_document(comparison_data: Dict):
    """비교 문서 생성"""
    handler = get_doc_generation_handler()
    return await handler.create_comparison_document(comparison_data)

# 문서 폼 생성 엔드포인트
@router.get("/documents/types")
async def get_document_types():
    """사용 가능한 문서 타입 목록 조회"""
    from modules import DocumentFormGenerator
    generator = DocumentFormGenerator()
    return {"success": True, "data": generator.get_document_types()}


@router.get("/documents/{document_type}/fields")
async def get_document_fields(document_type: str):
    """특정 문서 타입의 폼 필드 조회"""
    from modules import DocumentFormGenerator
    generator = DocumentFormGenerator()
    fields = generator.get_form_fields(document_type)
    if not fields:
        raise HTTPException(status_code=404, detail="문서 타입을 찾을 수 없습니다")
    return {"success": True, "data": fields}


@router.post("/documents/generate")
async def generate_document(request: Dict[str, Any]):
    """문서 생성 실행"""
    document_type = request.get("document_type")
    form_data = request.get("form_data", {})
    
    if not document_type:
        raise HTTPException(status_code=400, detail="문서 타입이 필요합니다")
    
    from modules import DocumentFormGenerator
    generator = DocumentFormGenerator()
    
    result = await generator.generate_document(document_type, form_data)
    return {"success": True, "data": result}


# 통합 조달 엔드포인트
@router.post("/procurement/complete")
async def complete_procurement_workflow(request: Dict[str, Any]):
    """전체 조달 워크플로우 실행"""
    query = request.get("query", "")
    requirements = request.get("requirements", {})
    
    # 1. 하이브리드 검색
    search_handler = get_hybrid_search_handler()
    search_results = await search_handler.search_all_platforms(query)
    
    if not search_results["success"]:
        raise HTTPException(status_code=500, detail="검색 실패")
    
    # 2. 매칭 분석
    all_products = []
    for platform_results in search_results["data"].values():
        if isinstance(platform_results, list):
            all_products.extend(platform_results)
    
    matching_results = await search_handler.analyze_procurement_match(all_products, requirements)
    
    # 3. 보고서 생성
    doc_handler = get_doc_generation_handler()
    report_results = await doc_handler.generate_procurement_report(all_products, requirements)
    
    return {
        "success": True,
        "search_results": search_results["data"],
        "matching_analysis": matching_results,
        "generated_report": report_results,
        "timestamp": datetime.now().isoformat()
    }
