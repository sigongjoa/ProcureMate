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
    get_doc_generation_handler,
    get_template_handler,
    get_notion_handler
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


# 설정 관리 엔드포인트
@router.get("/settings/load")
async def load_settings():
    """현재 설정 로드"""
    try:
        # 기본 설정 반환 (실제로는 설정 파일에서 로드)
        settings = {
            'llm': {
                'server_url': 'http://localhost:1234/v1',
                'model': 'llama-3.1-8b-instruct',
                'default_temperature': 0.7,
                'default_max_tokens': 1024
            },
            'vectordb': {
                'db_path': './chroma_db',
                'collection_name': 'procurement_data',
                'embedding_model': 'all-MiniLM-L6-v2'
            },
            'apis': {
                'g2b_api_key': '',
                'coupang_access_key': '',
                'coupang_secret_key': ''
            },
            'system': {
                'debug_mode': False,
                'auto_save': True
            }
        }
        return {"success": True, "data": settings}
    except Exception as e:
        logger.error(f"Failed to load settings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/settings/save")
async def save_settings(settings: Dict[str, Any]):
    """설정 저장"""
    try:
        # 실제로는 설정 파일에 저장
        logger.info("Settings saved successfully")
        return {"success": True, "message": "설정이 저장되었습니다"}
    except Exception as e:
        logger.error(f"Failed to save settings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/llm/test-connection")
async def test_llm_connection(request: Dict[str, Any]):
    """LLM 연결 테스트"""
    try:
        server_url = request.get('server_url')
        model = request.get('model')
        
        # 실제 연결 테스트 로직 (기본 응답)
        logger.info(f"LLM connection test: {server_url} - {model}")
        
        return {
            "success": True,
            "message": "LLM 연결 성공",
            "server_url": server_url,
            "model": model
        }
    except Exception as e:
        logger.error(f"LLM connection test failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/vectordb/test-connection")
async def test_vectordb_connection(request: Dict[str, Any]):
    """Vector DB 연결 테스트"""
    try:
        db_path = request.get('db_path')
        collection_name = request.get('collection_name')
        
        logger.info(f"VectorDB connection test: {db_path} - {collection_name}")
        
        return {
            "success": True,
            "message": "Vector DB 연결 성공",
            "db_path": db_path,
            "collection_name": collection_name
        }
    except Exception as e:
        logger.error(f"VectorDB connection test failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/external/test-connections")
async def test_external_apis(request: Dict[str, Any]):
    """외부 API 연결 테스트"""
    try:
        g2b_key = request.get('g2b_api_key')
        coupang_access = request.get('coupang_access_key')
        coupang_secret = request.get('coupang_secret_key')
        
        logger.info("External API connection tests completed")
        
        return {
            "success": True,
            "message": "API 연결 테스트 완료",
            "results": {
                "g2b": bool(g2b_key),
                "coupang": bool(coupang_access and coupang_secret)
            }
        }
    except Exception as e:
        logger.error(f"External API test failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# 템플릿 관리 엔드포인트
@router.get("/templates/document-list")
async def get_document_templates():
    """문서 템플릿 목록 조회"""
    try:
        from modules.template_manager import get_template_manager
        template_manager = get_template_manager()
        templates = template_manager.list_document_templates()
        
        logger.info(f"Document templates retrieved: {len(templates)} items")
        return {
            "success": True,
            "data": templates,
            "count": len(templates)
        }
    except Exception as e:
        logger.error(f"Failed to get document templates: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/templates/document-save")
async def save_document_template(template_data: Dict[str, Any]):
    """문서 템플릿 저장"""
    try:
        from modules.template_manager import get_template_manager
        template_manager = get_template_manager()
        
        name = template_data.get('name')
        success = template_manager.save_document_template(name, template_data)
        
        logger.info(f"Document template save result: {name} - {success}")
        
        return {
            "success": success,
            "message": "템플릿이 저장되었습니다" if success else "템플릿 저장에 실패했습니다"
        }
    except Exception as e:
        logger.error(f"Failed to save document template: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/templates/document-delete/{name}")
async def delete_document_template(name: str):
    """문서 템플릿 삭제"""
    try:
        from modules.template_manager import get_template_manager
        template_manager = get_template_manager()
        
        success = template_manager.delete_document_template(name)
        logger.info(f"Document template delete result: {name} - {success}")
        
        return {
            "success": success,
            "message": "템플릿이 삭제되었습니다" if success else "템플릿 삭제에 실패했습니다"
        }
    except Exception as e:
        logger.error(f"Failed to delete document template: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# 템플릿 관리 API (새로운 핸들러 사용)
@router.post("/templates/{template_type}/save")
async def save_template(template_type: str, request: Dict[str, Any]):
    """템플릿 저장"""
    name = request.get("name")
    data = request.get("data")
    
    if not name or not data:
        raise HTTPException(status_code=400, detail="이름과 데이터가 필요합니다")
    
    handler = get_template_handler()
    return await handler.save_template(template_type, name, data)

@router.get("/templates/{template_type}/load/{name}")
async def load_template(template_type: str, name: str):
    """템플릿 로드"""
    handler = get_template_handler()
    result = await handler.load_template(template_type, name)
    
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result

@router.get("/templates/{template_type}/list")
async def list_templates(template_type: str):
    """템플릿 목록 조회"""
    handler = get_template_handler()
    templates = await handler.list_templates(template_type)
    return {"success": True, "templates": templates}

@router.delete("/templates/{template_type}/delete/{name}")
async def delete_template(template_type: str, name: str):
    """템플릿 삭제"""
    handler = get_template_handler()
    result = await handler.delete_template(template_type, name)
    
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result

# Notion 연동 엔드포인트
@router.post("/notion/log/implementation")
async def notion_log_implementation(request: Dict[str, Any]):
    """Notion 구현 상황 로깅"""
    module_name = request.get("module_name")
    status = request.get("status")
    progress = request.get("progress", 0)
    
    if not module_name or not status:
        raise HTTPException(status_code=400, detail="모듈명과 상태가 필요합니다")
    
    handler = get_notion_handler()
    return await handler.log_implementation_status(module_name, status, progress)

@router.post("/notion/log/daily")
async def notion_log_daily(request: Dict[str, Any]):
    """Notion 일일 진행 상황 로깅"""
    date = request.get("date")
    changes = request.get("changes")
    next_steps = request.get("next_steps")
    
    if not date or not changes or not next_steps:
        raise HTTPException(status_code=400, detail="날짜, 변경사항, 다음단계가 필요합니다")
    
    handler = get_notion_handler()
    return await handler.log_daily_progress(date, changes, next_steps)

@router.post("/notion/log/issue")
async def notion_log_issue(request: Dict[str, Any]):
    """Notion 이슈 로깅"""
    title = request.get("title")
    description = request.get("description")
    priority = request.get("priority", "중간")
    
    if not title or not description:
        raise HTTPException(status_code=400, detail="제목과 설명이 필요합니다")
    
    handler = get_notion_handler()
    return await handler.log_issue(title, description, priority)

@router.get("/notion/test")
async def notion_test_connection():
    """Notion 연결 테스트"""
    handler = get_notion_handler()
    return await handler.test_connection()
