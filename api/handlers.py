#!/usr/bin/env python3
"""
API 요청 핸들러들
"""

import asyncio
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import json
import sys
from pathlib import Path

# 상위 디렉토리의 모듈들 import
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from utils import get_logger

logger = get_logger(__name__)

from modules.llm_module import LlmModule
from modules.vector_db_module import VectorDbModule
from modules.data_collector_module import DataCollectorModule
from modules.document_automation_module import DocumentAutomationModule
from modules.test_framework_module import TestFrameworkModule
from modules.g2b_api_client import G2BAPIClient
from modules.coupang_api_client import RateLimitedCoupangClient, CoupangAuth
from modules.advanced_rag_module import AdvancedVectorDbModule as AdvancedRAGModule
from modules.document_generator import ProcurementDocumentGenerator as DocumentGenerator
from modules.document_form_generator import DocumentFormGenerator

# CoupangAPIClient 별칭 생성 (기본 auth와 함께)
def create_coupang_client():
    import os
    auth = CoupangAuth(
        access_key=os.getenv("COUPANG_ACCESS_KEY", "test_key"),
        secret_key=os.getenv("COUPANG_SECRET_KEY", "test_secret"),
        vendor_id=os.getenv("COUPANG_VENDOR_ID", "test_vendor")
    )
    return RateLimitedCoupangClient(auth)

CoupangAPIClient = create_coupang_client

from .models import (
    LLMTestRequest, RAGTestRequest, WorkflowRequest,
    LLMTestResult, RAGTestResult, WorkflowTestResult,
    TestResult, TestMetrics, SystemStatus, ModuleStatus
)

# 공유 모듈 인스턴스 (싱글톤 패턴)
_shared_modules = None

def get_shared_modules():
    """공유 모듈 인스턴스 반환 (싱글톤)"""
    global _shared_modules
    if _shared_modules is None:
        logger.info("전역 모듈 인스턴스 생성")
        
        _shared_modules = {
            "llm": LlmModule(),
            "vector_db": VectorDbModule(),
            "data_collector": DataCollectorModule(),
            "document": DocumentAutomationModule(),
            "test_framework": TestFrameworkModule(),
            "g2b_api": G2BAPIClient(),
            "coupang_api": CoupangAPIClient(),
            "advanced_rag": AdvancedRAGModule(),
            "doc_generator": DocumentGenerator(),
            "document_form_generator": DocumentFormGenerator()
        }
        
        logger.info(f"전역 모듈 초기화 완료: {len(_shared_modules)}개 모듈")
        
    return _shared_modules

class BaseHandler:
    """기본 핸들러 클래스"""
    
    def __init__(self):
        self.test_results: List[TestResult] = []
        # 공유 모듈 인스턴스 사용
        self.modules = get_shared_modules()
    
    def _generate_test_id(self) -> str:
        """테스트 ID 생성"""
        return str(uuid.uuid4())
    
    def _create_test_metrics(self, response_time: float, **kwargs) -> TestMetrics:
        """테스트 메트릭 생성"""
        return TestMetrics(
            response_time=response_time,
            quality_score=kwargs.get('quality_score'),
            success_rate=kwargs.get('success_rate'),
            error_count=kwargs.get('error_count', 0),
            additional_metrics=kwargs.get('additional_metrics', {})
        )

class LLMTestHandler(BaseHandler):
    """LLM 테스트 핸들러"""
    
    async def run_test(self, request: LLMTestRequest) -> LLMTestResult:
        """LLM 테스트 실행"""
        start_time = time.time()
        test_id = self._generate_test_id()
        
        llm_module = self.modules.get("llm")
        if not llm_module:
            raise Exception("LLM 모듈이 초기화되지 않음")
        
        # 설정 임시 적용
        original_temp = llm_module.temperature
        original_max_tokens = llm_module.max_tokens
        
        llm_module.temperature = request.temperature
        llm_module.max_tokens = request.max_tokens
        
        # AI 분석 실행
        analysis_result = llm_module.analyze_procurement_request(request.query)
        
        # 원래 설정 복원
        llm_module.temperature = original_temp
        llm_module.max_tokens = original_max_tokens
        
        response_time = time.time() - start_time
        
        # 응답 품질 평가
        quality_score = self._evaluate_llm_response(request.query, analysis_result)
        
        # 메트릭 생성
        metrics = self._create_test_metrics(
            response_time=response_time,
            quality_score=quality_score,
            additional_metrics={
                "has_items": len(analysis_result.get("items", [])) > 0,
                "has_quantities": len(analysis_result.get("quantities", [])) > 0,
                "json_valid": isinstance(analysis_result, dict),
                "temperature": request.temperature,
                "max_tokens": request.max_tokens
            }
        )
        
        # 테스트 결과 저장
        test_result = TestResult(
            id=test_id,
            test_type="llm_analysis",
            status="completed", 
            timestamp=datetime.now(),
            input_data=request.dict(),
            output_data=analysis_result,
            metrics=metrics,
            duration=response_time
        )
        
        self.test_results.append(test_result)
        
        return LLMTestResult(
            success=True,
            result=analysis_result,
            metrics=metrics,
            timestamp=datetime.now()
        )
    
    def _evaluate_llm_response(self, query: str, response: Dict[str, Any]) -> float:
        """LLM 응답 품질 평가"""
        score = 0.0
        
        # 기본 구조 체크
        if isinstance(response, dict):
            score += 2.0
            if "items" in response and response["items"]:
                score += 2.0
            if "quantities" in response and response["quantities"]:
                score += 1.0
            if "urgency" in response:
                score += 1.0
        
        # 내용 품질 체크
        items = response.get("items", [])
        if items:
            query_words = set(query.lower().split())
            for item in items:
                item_words = set(item.lower().split())
                if query_words & item_words:
                    score += 1.0
            
            quantities = response.get("quantities", [])
            if len(quantities) == len(items):
                score += 1.0
                
            if response.get("budget_range") and response["budget_range"] != "미정":
                score += 1.0
        
        return min(score, 10.0)

class RAGTestHandler(BaseHandler):
    """RAG 테스트 핸들러"""
    
    async def run_test(self, request: RAGTestRequest) -> RAGTestResult:
        """RAG 테스트 실행"""
        start_time = time.time()
        test_id = self._generate_test_id()
        
        vector_db = self.modules.get("vector_db")
        if not vector_db:
            raise Exception("VectorDB 모듈이 초기화되지 않음")
        
        # 벡터 검색 실행
        search_results = vector_db.search_similar_products(
            request.query, 
            request.limit
        )
        
        response_time = time.time() - start_time
        
        # 검색 품질 메트릭 계산
        similarities = [
            (1 - r.get("distance", 1)) if "distance" in r else 0 
            for r in search_results
        ]
        avg_similarity = sum(similarities) / len(similarities) if similarities else 0
        
        metrics = self._create_test_metrics(
            response_time=response_time,
            quality_score=avg_similarity * 10,
            additional_metrics={
                "results_count": len(search_results),
                "avg_similarity": avg_similarity,
                "max_similarity": max(similarities) if similarities else 0,
                "min_similarity": min(similarities) if similarities else 0,
                "has_metadata": all("metadata" in r for r in search_results)
            }
        )
        
        test_result = TestResult(
            id=test_id,
            test_type="rag_search",
            status="completed",
            timestamp=datetime.now(),
            input_data=request.dict(),
            output_data={"results": search_results},
            metrics=metrics,
            duration=response_time
        )
        
        self.test_results.append(test_result)
        
        return RAGTestResult(
            success=True,
            results=search_results,
            metrics=metrics,
            timestamp=datetime.now()
        )

class WorkflowTestHandler(BaseHandler):
    """워크플로우 테스트 핸들러"""
    
    async def run_test(self, request: WorkflowRequest) -> WorkflowTestResult:
        """전체 워크플로우 테스트"""
        start_time = time.time()
        test_id = self._generate_test_id()
        workflow_results = {}
        
        query = request.query
        
        # 1단계: LLM 분석
        logger.info("워크플로우 1단계: LLM 분석")
        llm_start = time.time()
        llm_module = self.modules["llm"]
        analysis = llm_module.analyze_procurement_request(query)
        
        workflow_results["llm_analysis"] = {
            "step_name": "LLM 분석",
            "success": True,
            "result": analysis,
            "duration": time.time() - llm_start
        }
        
        # 2단계: 데이터 수집 (옵션)
        if request.enable_data_collection:
            logger.info("워크플로우 2단계: 데이터 수집")
            data_start = time.time()
            data_collector = self.modules["data_collector"]
            search_results = {}
            
            for item in analysis.get("items", [])[:2]:  # 최대 2개 항목
                item_results = data_collector.search_all_platforms(
                    item, 
                    limit_per_platform=request.max_items_per_platform
                )
                search_results[item] = item_results
            
            workflow_results["data_collection"] = {
                "step_name": "데이터 수집",
                "success": True,
                "result": search_results,
                "duration": time.time() - data_start
            }
        
        # 3단계: RAG 검색 (옵션)
        if request.enable_rag_search:
            logger.info("워크플로우 3단계: RAG 검색")
            rag_start = time.time()
            vector_db = self.modules["vector_db"]
            
            similar_products = vector_db.search_similar_products(query, limit=3)
            similar_cases = vector_db.find_similar_procurement_cases(analysis, limit=2)
            
            workflow_results["rag_search"] = {
                "step_name": "RAG 검색",
                "success": True,
                "result": {
                    "similar_products": similar_products,
                    "similar_cases": similar_cases
                },
                "duration": time.time() - rag_start
            }
        
        # 4단계: 문서 생성 (옵션)
        if request.enable_document_generation:
            logger.info("워크플로우 4단계: 문서 생성")
            doc_start = time.time()
            doc_module = self.modules["document"]
            
            # 통합 검색 결과 준비
            all_search_results = {}
            if "data_collection" in workflow_results:
                for item_results in workflow_results["data_collection"]["result"].values():
                    for platform, products in item_results.items():
                        if platform not in all_search_results:
                            all_search_results[platform] = []
                        all_search_results[platform].extend(products)
            
            documents = doc_module.create_procurement_document_package(
                analysis,
                all_search_results,
                "AI 기반 워크플로우 테스트"
            )
            
            workflow_results["document_generation"] = {
                "step_name": "문서 생성",
                "success": True,
                "result": documents,
                "duration": time.time() - doc_start
            }
        
        total_time = time.time() - start_time
        
        # 전체 메트릭 계산
        step_times = {
            step: data["duration"] 
            for step, data in workflow_results.items()
        }
        
        metrics = self._create_test_metrics(
            response_time=total_time,
            quality_score=8.0,  # 워크플로우 완료시 기본 점수
            additional_metrics={
                "total_time": total_time,
                "success_stages": len(workflow_results),
                "step_times": step_times,
                **step_times
            }
        )
        
        test_result = TestResult(
            id=test_id,
            test_type="full_workflow",
            status="completed",
            timestamp=datetime.now(),
            input_data=request.dict(),
            output_data=workflow_results,
            metrics=metrics,
            duration=total_time
        )
        
        self.test_results.append(test_result)
        
        return WorkflowTestResult(
            success=True,
            workflow_results=workflow_results,
            metrics=metrics,
            timestamp=datetime.now()
        )

class G2BAPIHandler(BaseHandler):
    """G2B API 핸들러"""
    
    async def search_bid_announcements(self, query_params: Dict[str, Any]) -> Dict[str, Any]:
        """입찰공고 검색"""
        start_time = time.time()
        
        g2b_client = self.modules["g2b_api"]
        announcements = await g2b_client.get_bid_announcements(query_params)
        
        response_time = time.time() - start_time
        
        return {
            "success": True,
            "data": announcements,
            "total_count": len(announcements.get("items", [])),
            "response_time": response_time
        }
    
    async def get_contract_info(self, contract_id: str) -> Dict[str, Any]:
        """계약정보 조회"""
        start_time = time.time()
        
        g2b_client = self.modules["g2b_api"]
        contract_info = await g2b_client.get_contract_info({"contractId": contract_id})
        
        return {
            "success": True,
            "data": contract_info,
            "response_time": time.time() - start_time
        }

class CoupangAPIHandler(BaseHandler):
    """쿠팡 API 핸들러"""
    
    async def search_products(self, query: str, limit: int = 20) -> Dict[str, Any]:
        """쿠팡 상품 검색"""
        start_time = time.time()
        
        coupang_client = self.modules["coupang_api"]
        products = await coupang_client.search_products(query, limit)
        
        response_time = time.time() - start_time
        
        return {
            "success": True,
            "data": products,
            "total_count": len(products),
            "response_time": response_time
        }
    
    async def get_product_details(self, product_id: str) -> Dict[str, Any]:
        """쿠팡 상품 상세정보 조회"""
        start_time = time.time()
        
        coupang_client = self.modules["coupang_api"]
        product_details = await coupang_client.get_product_details(product_id)
        
        return {
            "success": True,
            "data": product_details,
            "response_time": time.time() - start_time
        }

class HybridSearchHandler(BaseHandler):
    """하이브리드 검색 핸들러"""
    
    async def search_all_platforms(self, query: str, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """모든 플랫폼 통합 검색"""
        start_time = time.time()
        
        advanced_rag = self.modules["advanced_rag"]
        g2b_client = self.modules["g2b_api"]
        coupang_client = self.modules["coupang_api"]
        
        # 병렬 검색 실행
        tasks = [
            advanced_rag.hybrid_search(query, k=10),
            g2b_client.search_products({"query": query, "limit": 10}),
            coupang_client.search_products(query, limit=10)
        ]
        
        rag_results, g2b_results, coupang_results = await asyncio.gather(*tasks)
        
        # 결과 통합 및 정규화
        unified_results = {
            "rag_search": rag_results,
            "g2b_products": g2b_results,
            "coupang_products": coupang_results,
            "total_found": len(rag_results) + len(g2b_results) + len(coupang_results)
        }
        
        response_time = time.time() - start_time
        
        return {
            "success": True,
            "data": unified_results,
            "response_time": response_time
        }
    
    async def analyze_procurement_match(self, products: List[Dict], requirements: Dict) -> Dict[str, Any]:
        """조달 요구사항 매칭 분석"""
        start_time = time.time()
        
        advanced_rag = self.modules["advanced_rag"]
        matching_results = await advanced_rag.match_products_to_requirements(products, requirements)
        
        return {
            "success": True,
            "data": matching_results,
            "response_time": time.time() - start_time
        }

class DocumentGenerationHandler(BaseHandler):
    """자동 문서 생성 핸들러"""
    
    async def generate_procurement_report(self, products: List[Dict], requirements: Dict) -> Dict[str, Any]:
        """조달 보고서 자동 생성"""
        start_time = time.time()
        
        doc_generator = self.modules["doc_generator"]
        llm_module = self.modules["llm"]
        
        # LLM을 활용한 자동 보고서 생성
        report = await doc_generator.generate_procurement_report(
            products, requirements, llm_module
        )
        
        return {
            "success": True,
            "data": report,
            "response_time": time.time() - start_time
        }
    
    async def create_comparison_document(self, comparison_data: Dict) -> Dict[str, Any]:
        """비교 문서 생성"""
        start_time = time.time()
        
        doc_generator = self.modules["doc_generator"]
        comparison_doc = await doc_generator.create_comparison_document(comparison_data)
        
        return {
            "success": True,
            "data": comparison_doc,
            "response_time": time.time() - start_time
        }

class SystemStatusHandler(BaseHandler):
    """시스템 상태 핸들러"""
    
    async def get_status(self) -> SystemStatus:
        """시스템 상태 조회"""
        # 각 모듈 상태 체크
        modules_status = {}
        
        for module_name, module in self.modules.items():
            if module_name == "llm":
                is_healthy = module.check_server_health()
            elif module_name == "vector_db":
                is_healthy = module.client is not None
            else:
                is_healthy = True  # 기본적으로 사용 가능하다고 가정
            
            modules_status[module_name] = ModuleStatus(
                name=module_name,
                status="healthy" if is_healthy else "unhealthy",
                last_check=datetime.now(),
                details={"initialized": True}
            )
        
        # 전체 상태 계산
        llm_connected = modules_status.get("llm", {}).status == "healthy" if "llm" in modules_status else False
        vector_db_ready = modules_status.get("vector_db", {}).status == "healthy" if "vector_db" in modules_status else False
        
        last_test = None
        if self.test_results:
            last_test = max(test.timestamp for test in self.test_results)
        
        return SystemStatus(
            llm_connected=llm_connected,
            vector_db_ready=vector_db_ready,
            total_tests=len(self.test_results),
            last_test=last_test,
            modules=modules_status,
            system_info={
                "uptime": "실행 중",
                "version": "1.0.0",
                "python_version": sys.version
            }
        )
    
    async def get_test_history(self, limit: int = 50, test_type: Optional[str] = None) -> Dict[str, Any]:
        """테스트 이력 조회"""
        filtered_tests = self.test_results
        
        if test_type:
            filtered_tests = [t for t in filtered_tests if t.test_type == test_type]
        
        # 최신순 정렬
        filtered_tests.sort(key=lambda x: x.timestamp, reverse=True)
        
        return {
            "tests": [
                {
                    "id": test.id,
                    "type": test.test_type,
                    "status": test.status,
                    "timestamp": test.timestamp.isoformat(),
                    "duration": test.duration,
                    "success": test.status == "completed"
                }
                for test in filtered_tests[:limit]
            ],
            "total": len(filtered_tests),
            "page_size": limit
        }
    
    async def get_test_detail(self, test_id: str) -> Optional[TestResult]:
        """테스트 상세 조회"""
        for test in self.test_results:
            if test.id == test_id:
                return test
        return None
    
    async def delete_test(self, test_id: str) -> bool:
        """테스트 삭제"""
        for i, test in enumerate(self.test_results):
            if test.id == test_id:
                del self.test_results[i]
                return True
        return False
    
    async def get_performance_analytics(self, days: int = 7) -> Dict[str, Any]:
        """성능 분석 데이터"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 기간 내 테스트 필터링
        period_tests = [
            test for test in self.test_results
            if start_date <= test.timestamp <= end_date
        ]
        
        if not period_tests:
            return {
                "period_start": start_date.isoformat(),
                "period_end": end_date.isoformat(),
                "total_tests": 0,
                "success_rate": 0.0,
                "avg_response_time": 0.0,
                "test_type_breakdown": {},
                "performance_trends": {},
                "top_errors": []
            }
        
        # 성공률 계산
        successful_tests = [t for t in period_tests if t.status == "completed"]
        success_rate = len(successful_tests) / len(period_tests) * 100
        
        # 평균 응답 시간
        avg_response_time = sum(t.metrics.response_time for t in period_tests) / len(period_tests)
        
        # 테스트 타입별 분포
        test_type_breakdown = {}
        for test in period_tests:
            test_type_breakdown[test.test_type] = test_type_breakdown.get(test.test_type, 0) + 1
        
        # 성능 트렌드 (일별)
        daily_times = {}
        for test in period_tests:
            day = test.timestamp.date().isoformat()
            if day not in daily_times:
                daily_times[day] = []
            daily_times[day].append(test.metrics.response_time)
        
        performance_trends = {
            day: sum(times) / len(times)
            for day, times in daily_times.items()
        }
        
        # 주요 오류
        error_tests = [t for t in period_tests if t.status == "failed"]
        error_counts = {}
        for test in error_tests:
            error = test.error_message or "Unknown error"
            error_counts[error] = error_counts.get(error, 0) + 1
        
        top_errors = [
            {"error": error, "count": count}
            for error, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
        
        return {
            "period_start": start_date.isoformat(),
            "period_end": end_date.isoformat(),
            "total_tests": len(period_tests),
            "success_rate": success_rate,
            "avg_response_time": avg_response_time,
            "test_type_breakdown": test_type_breakdown,
            "performance_trends": performance_trends,
            "top_errors": top_errors
        }
    
    async def get_config(self) -> Dict[str, Any]:
        """현재 설정 조회"""
        return {
            "llm": {
                "model_name": "gpt-3.5-turbo",
                "temperature": 0.7,
                "max_tokens": 512
            },
            "rag": {
                "default_limit": 5,
                "similarity_threshold": 0.0
            },
            "system": {
                "max_concurrent_tests": 5,
                "test_retention_days": 30
            }
        }
    
    async def update_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """설정 업데이트"""
        # 실제 구현에서는 설정 파일이나 데이터베이스에 저장
        logger.info(f"설정 업데이트 요청: {config}")
        return {"success": True, "message": "설정이 업데이트되었습니다"}
    
    async def reset_system(self) -> Dict[str, Any]:
        """시스템 초기화"""
        self.test_results.clear()
        logger.info("시스템이 초기화되었습니다")
        return {"success": True, "message": "시스템이 초기화되었습니다"}

# 전역 핸들러 인스턴스들 (싱글톤 패턴)
_llm_handler = None
_rag_handler = None
_workflow_handler = None
_status_handler = None
_g2b_handler = None
_coupang_handler = None
_hybrid_search_handler = None
_doc_generation_handler = None


def get_llm_handler() -> LLMTestHandler:
    """LLM 핸들러 싱글톤"""
    global _llm_handler
    if _llm_handler is None:
        _llm_handler = LLMTestHandler()
    return _llm_handler

def get_rag_handler() -> RAGTestHandler:
    """RAG 핸들러 싱글톤"""
    global _rag_handler
    if _rag_handler is None:
        _rag_handler = RAGTestHandler()
    return _rag_handler

def get_workflow_handler() -> WorkflowTestHandler:
    """워크플로우 핸들러 싱글톤"""
    global _workflow_handler
    if _workflow_handler is None:
        _workflow_handler = WorkflowTestHandler()
    return _workflow_handler

def get_status_handler() -> SystemStatusHandler:
    """상태 핸들러 싱글톤"""
    global _status_handler
    if _status_handler is None:
        _status_handler = SystemStatusHandler()
    return _status_handler

def get_g2b_handler() -> G2BAPIHandler:
    """G2B API 핸들러 싱글톤"""
    global _g2b_handler
    if _g2b_handler is None:
        _g2b_handler = G2BAPIHandler()
    return _g2b_handler

def get_coupang_handler() -> CoupangAPIHandler:
    """쿠팡 API 핸들러 싱글톤"""
    global _coupang_handler
    if _coupang_handler is None:
        _coupang_handler = CoupangAPIHandler()
    return _coupang_handler

def get_hybrid_search_handler() -> HybridSearchHandler:
    """하이브리드 검색 핸들러 싱글톤"""
    global _hybrid_search_handler
    if _hybrid_search_handler is None:
        _hybrid_search_handler = HybridSearchHandler()
    return _hybrid_search_handler

def get_doc_generation_handler() -> DocumentGenerationHandler:
    """문서 생성 핸들러 싱글톤"""
    global _doc_generation_handler
    if _doc_generation_handler is None:
        _doc_generation_handler = DocumentGenerationHandler()
    return _doc_generation_handler
