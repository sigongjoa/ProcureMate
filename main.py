#!/usr/bin/env python3
"""
ProcureMate GUI - 성능 테스트 & 튜닝 웹 인터페이스
LLM과 RAG 시스템의 실시간 테스트 및 성능 분석을 위한 웹 GUI
"""

import asyncio
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path
import sys
import json

# 상위 디렉토리의 모듈들 import를 위한 경로 추가
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent))  # 현재 gui 디렉토리도 추가

from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
from api import router as api_router
from api.handlers import get_status_handler

from utils import get_logger
from utils.json_utils import serialize_for_websocket

logger = get_logger(__name__)

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 라이프사이클 관리"""
    # Startup
    logger.info("ProcureMate GUI 시작")
    yield
    # Shutdown
    logger.info("ProcureMate GUI 종료")

# FastAPI 앱 초기화
app = FastAPI(
    title="ProcureMate GUI",
    description="LLM & RAG 성능 테스트 및 튜닝 인터페이스",
    version="1.0.0",
    lifespan=lifespan
)

# API 라우터 등록
app.include_router(api_router)

# 정적 파일 및 템플릿 설정
current_dir = Path(__file__).parent
static_path = current_dir / "static"
templates_path = current_dir / "templates"

# 디렉토리 존재 확인 및 생성
if not static_path.exists():
    static_path.mkdir(exist_ok=True)
    logger.info(f"static 디렉토리 생성: {static_path}")

if not templates_path.exists():
    templates_path.mkdir(exist_ok=True)
    logger.info(f"templates 디렉토리 생성: {templates_path}")

app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
templates = Jinja2Templates(directory=str(templates_path))

# WebSocket 연결 관리
connected_clients: List[WebSocket] = []

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """메인 대시보드 페이지"""
    # 시스템 상태 체크
    status_handler = get_status_handler()
    system_status = await status_handler.get_status()
    
    return templates.TemplateResponse(
        "index.html", 
        {
            "request": request,
            "system_status": system_status,
            "recent_tests": status_handler.test_results[-10:] if status_handler.test_results else []
        }
    )

@app.get("/llm-test", response_class=HTMLResponse)
async def llm_test_page(request: Request):
    """LLM 테스트 페이지"""
    return templates.TemplateResponse("llm_test.html", {"request": request})

@app.get("/rag-analysis", response_class=HTMLResponse)
async def rag_analysis_page(request: Request):
    """RAG 분석 페이지"""
    return templates.TemplateResponse("rag_analysis.html", {"request": request})

@app.get("/workflow", response_class=HTMLResponse)
async def workflow_page(request: Request):
    """워크플로우 테스트 페이지"""
    return templates.TemplateResponse("workflow.html", {"request": request})

@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    """향상된 설정 페이지"""
    return templates.TemplateResponse("settings.html", {"request": request})

@app.get("/document-generator", response_class=HTMLResponse)
async def document_generator_page(request: Request):
    """기본 문서 생성기 페이지"""
    return templates.TemplateResponse("document_generator.html", {"request": request})

@app.get("/enhanced-document-generator", response_class=HTMLResponse)
async def enhanced_document_generator_page(request: Request):
    """향상된 문서 생성기 페이지"""
    return templates.TemplateResponse("enhanced_document_generator.html", {"request": request})

@app.get("/g2b-test", response_class=HTMLResponse)
async def g2b_test_page(request: Request):
    """G2B 테스트 페이지"""
    return templates.TemplateResponse("g2b_test.html", {"request": request})

@app.get("/coupang-test", response_class=HTMLResponse)
async def coupang_test_page(request: Request):
    """쿠팡 테스트 페이지"""
    return templates.TemplateResponse("coupang_test.html", {"request": request})

# WebSocket 연결 관리
async def broadcast_message(message: Dict[str, Any]):
    """모든 연결된 클라이언트에게 메시지 브로드캐스트"""
    if connected_clients:
        disconnected_clients = []
        for client in connected_clients:
            try:
                await client.send_json(message)
            except:
                disconnected_clients.append(client)
        
        # 연결이 끊어진 클라이언트 제거
        for client in disconnected_clients:
            connected_clients.remove(client)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """실시간 업데이트를 위한 WebSocket"""
    await websocket.accept()
    connected_clients.append(websocket)
    
    status_handler = get_status_handler()
    
    while True:
        # 주기적으로 시스템 상태 전송
        status = await status_handler.get_status()
        status_data = serialize_for_websocket(status.dict())
        
        await websocket.send_text(json.dumps({
            "type": "status_update",
            "data": status_data
        }, ensure_ascii=False))
        
        # 최근 테스트 결과 전송
        if status_handler.test_results:
            latest_test = status_handler.test_results[-1]
            test_data = {
                "timestamp": latest_test.timestamp.isoformat(),
                "type": latest_test.test_type,
                "success": latest_test.status == "completed",
                "metrics": serialize_for_websocket(latest_test.metrics.dict()),
                "output_preview": str(latest_test.output_data)[:200] if latest_test.output_data else None
            }
            
            await websocket.send_text(json.dumps({
                "type": "test_update",
                "data": test_data
            }, ensure_ascii=False))
        
        await asyncio.sleep(5)  # 5초마다 업데이트


if __name__ == "__main__":
    logger.info("ProcureMate GUI 서버 시작")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8081,
        reload=True,
        log_level="info"
    )
