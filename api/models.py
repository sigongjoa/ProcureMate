#!/usr/bin/env python3
"""
API 데이터 모델 정의
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from enum import Enum

class TestType(str, Enum):
    """테스트 타입"""
    LLM_ANALYSIS = "llm_analysis"
    RAG_SEARCH = "rag_search"
    FULL_WORKFLOW = "full_workflow"
    DATA_COLLECTION = "data_collection"
    DOCUMENT_GENERATION = "document_generation"

class TestStatus(str, Enum):
    """테스트 상태"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

# 요청 모델들
class LLMTestRequest(BaseModel):
    """LLM 테스트 요청"""
    query: str = Field(..., description="분석할 조달 요청")
    temperature: float = Field(0.7, ge=0.0, le=1.0, description="모델 온도")
    max_tokens: int = Field(512, ge=1, le=4096, description="최대 토큰 수")
    model_name: Optional[str] = Field(None, description="사용할 모델명")

class RAGTestRequest(BaseModel):
    """RAG 테스트 요청"""
    query: str = Field(..., description="검색 쿼리")
    limit: int = Field(5, ge=1, le=50, description="검색 결과 수")
    collection_name: Optional[str] = Field(None, description="컬렉션명")
    similarity_threshold: float = Field(0.0, ge=0.0, le=1.0, description="유사도 임계값")

class WorkflowRequest(BaseModel):
    """워크플로우 테스트 요청"""
    query: str = Field(..., description="조달 요청")
    enable_data_collection: bool = Field(True, description="데이터 수집 활성화")
    enable_rag_search: bool = Field(True, description="RAG 검색 활성화")
    enable_document_generation: bool = Field(True, description="문서 생성 활성화")
    max_items_per_platform: int = Field(3, description="플랫폼당 최대 수집 아이템")

# 응답 모델들
class TestMetrics(BaseModel):
    """테스트 메트릭"""
    response_time: float = Field(..., description="응답 시간(초)")
    quality_score: Optional[float] = Field(None, description="품질 점수")
    success_rate: Optional[float] = Field(None, description="성공률")
    error_count: int = Field(0, description="오류 횟수")
    additional_metrics: Dict[str, Any] = Field(default_factory=dict, description="추가 메트릭")

class TestResult(BaseModel):
    """테스트 결과"""
    id: str = Field(..., description="테스트 ID")
    test_type: TestType = Field(..., description="테스트 타입")
    status: TestStatus = Field(..., description="테스트 상태")
    timestamp: datetime = Field(..., description="실행 시간")
    input_data: Dict[str, Any] = Field(..., description="입력 데이터")
    output_data: Optional[Dict[str, Any]] = Field(None, description="출력 데이터")
    metrics: TestMetrics = Field(..., description="성능 메트릭")
    error_message: Optional[str] = Field(None, description="오류 메시지")
    duration: float = Field(..., description="실행 시간(초)")

class LLMTestResult(BaseModel):
    """LLM 테스트 결과"""
    success: bool = Field(..., description="성공 여부")
    result: Optional[Dict[str, Any]] = Field(None, description="분석 결과")
    metrics: TestMetrics = Field(..., description="성능 메트릭")
    timestamp: datetime = Field(..., description="실행 시간")
    error: Optional[str] = Field(None, description="오류 메시지")

class RAGTestResult(BaseModel):
    """RAG 테스트 결과"""
    success: bool = Field(..., description="성공 여부")
    results: Optional[List[Dict[str, Any]]] = Field(None, description="검색 결과")
    metrics: TestMetrics = Field(..., description="성능 메트릭")
    timestamp: datetime = Field(..., description="실행 시간")
    error: Optional[str] = Field(None, description="오류 메시지")

class WorkflowStepResult(BaseModel):
    """워크플로우 단계 결과"""
    step_name: str = Field(..., description="단계명")
    success: bool = Field(..., description="성공 여부")
    result: Optional[Dict[str, Any]] = Field(None, description="단계 결과")
    duration: float = Field(..., description="실행 시간(초)")
    error: Optional[str] = Field(None, description="오류 메시지")

class WorkflowTestResult(BaseModel):
    """워크플로우 테스트 결과"""
    success: bool = Field(..., description="전체 성공 여부")
    workflow_results: Dict[str, WorkflowStepResult] = Field(..., description="단계별 결과")
    metrics: TestMetrics = Field(..., description="전체 메트릭")
    timestamp: datetime = Field(..., description="실행 시간")
    error: Optional[str] = Field(None, description="오류 메시지")

# 시스템 상태 모델
class ModuleStatus(BaseModel):
    """모듈 상태"""
    name: str = Field(..., description="모듈명")
    status: str = Field(..., description="상태")
    last_check: datetime = Field(..., description="마지막 체크 시간")
    error: Optional[str] = Field(None, description="오류 메시지")
    details: Dict[str, Any] = Field(default_factory=dict, description="상세 정보")

class SystemStatus(BaseModel):
    """시스템 전체 상태"""
    llm_connected: bool = Field(..., description="LLM 연결 상태")
    vector_db_ready: bool = Field(..., description="Vector DB 준비 상태")
    total_tests: int = Field(..., description="총 테스트 수")
    last_test: Optional[datetime] = Field(None, description="마지막 테스트 시간")
    modules: Dict[str, ModuleStatus] = Field(..., description="모듈별 상태")
    system_info: Dict[str, Any] = Field(default_factory=dict, description="시스템 정보")

# 설정 모델
class LLMConfig(BaseModel):
    """LLM 설정"""
    model_name: str = Field("gpt-3.5-turbo", description="모델명")
    temperature: float = Field(0.7, description="기본 온도")
    max_tokens: int = Field(512, description="기본 최대 토큰")
    timeout: int = Field(30, description="타임아웃(초)")

class RAGConfig(BaseModel):
    """RAG 설정"""
    default_limit: int = Field(5, description="기본 검색 결과 수")
    similarity_threshold: float = Field(0.0, description="유사도 임계값")
    collection_name: Optional[str] = Field(None, description="기본 컬렉션명")

class SystemConfig(BaseModel):
    """시스템 설정"""
    llm: LLMConfig = Field(default_factory=LLMConfig)
    rag: RAGConfig = Field(default_factory=RAGConfig)
    max_concurrent_tests: int = Field(5, description="최대 동시 테스트 수")
    test_retention_days: int = Field(30, description="테스트 결과 보관 일수")
    enable_websocket: bool = Field(True, description="WebSocket 활성화")
    log_level: str = Field("INFO", description="로그 레벨")

# 분석 모델
class PerformanceAnalytics(BaseModel):
    """성능 분석 데이터"""
    period_start: datetime = Field(..., description="분석 시작 시간")
    period_end: datetime = Field(..., description="분석 종료 시간")
    total_tests: int = Field(..., description="총 테스트 수")
    success_rate: float = Field(..., description="성공률")
    avg_response_time: float = Field(..., description="평균 응답 시간")
    test_type_breakdown: Dict[str, int] = Field(..., description="테스트 타입별 분포")
    performance_trends: Dict[str, List[float]] = Field(..., description="성능 트렌드")
    top_errors: List[Dict[str, Any]] = Field(..., description="주요 오류")

# WebSocket 메시지 모델
class WebSocketMessage(BaseModel):
    """WebSocket 메시지"""
    type: str = Field(..., description="메시지 타입")
    data: Dict[str, Any] = Field(..., description="메시지 데이터")
    timestamp: datetime = Field(default_factory=datetime.now, description="시간")

# 응답 래퍼
class APIResponse(BaseModel):
    """API 응답 래퍼"""
    success: bool = Field(..., description="성공 여부")
    data: Optional[Any] = Field(None, description="응답 데이터")
    message: Optional[str] = Field(None, description="메시지")
    error: Optional[str] = Field(None, description="오류 메시지")
    timestamp: datetime = Field(default_factory=datetime.now, description="응답 시간")

# 페이징 모델
class PaginationInfo(BaseModel):
    """페이징 정보"""
    total: int = Field(..., description="전체 항목 수")
    page: int = Field(..., description="현재 페이지")
    page_size: int = Field(..., description="페이지 크기")
    total_pages: int = Field(..., description="전체 페이지 수")
    has_next: bool = Field(..., description="다음 페이지 존재 여부")
    has_prev: bool = Field(..., description="이전 페이지 존재 여부")

class PaginatedResponse(BaseModel):
    """페이징된 응답"""
    items: List[Any] = Field(..., description="항목들")
    pagination: PaginationInfo = Field(..., description="페이징 정보")
