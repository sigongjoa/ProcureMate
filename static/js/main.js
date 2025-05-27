// ProcureMate GUI 메인 JavaScript

class ProcureMateGUI {
    constructor() {
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 3000;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.connectWebSocket();
        this.loadSystemStatus();
    }
    
    // 이벤트 리스너 설정
    setupEventListeners() {
        // 페이지 언로드시 WebSocket 연결 해제
        window.addEventListener('beforeunload', () => {
            if (this.ws) {
                this.ws.close();
            }
        });
        
        // 온라인/오프라인 이벤트
        window.addEventListener('online', () => {
            this.updateConnectionStatus(true);
            this.connectWebSocket();
        });
        
        window.addEventListener('offline', () => {
            this.updateConnectionStatus(false);
        });
        
        // 키보드 단축키
        document.addEventListener('keydown', (e) => {
            // Ctrl + R로 시스템 상태 새로고침
            if (e.ctrlKey && e.key === 'r') {
                e.preventDefault();
                this.loadSystemStatus();
            }
        });
    }
    
    // WebSocket 연결
    connectWebSocket() {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            return;
        }
        
        try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws`;
            
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = () => {
                console.log('WebSocket 연결됨');
                this.updateConnectionStatus(true);
                this.reconnectAttempts = 0;
            };
            
            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleWebSocketMessage(data);
                } catch (error) {
                    console.error('WebSocket 메시지 파싱 오류:', error);
                }
            };
            
            this.ws.onclose = () => {
                console.log('WebSocket 연결 해제됨');
                this.updateConnectionStatus(false);
                this.scheduleReconnect();
            };
            
            this.ws.onerror = (error) => {
                console.error('WebSocket 오류:', error);
                this.updateConnectionStatus(false);
            };
            
        } catch (error) {
            console.error('WebSocket 연결 실패:', error);
            this.updateConnectionStatus(false);
            this.scheduleReconnect();
        }
    }
    
    // WebSocket 재연결 스케줄링
    scheduleReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`${this.reconnectDelay / 1000}초 후 재연결 시도 (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
            
            setTimeout(() => {
                this.connectWebSocket();
            }, this.reconnectDelay);
            
            // 재연결 지연 시간 증가 (백오프)
            this.reconnectDelay = Math.min(this.reconnectDelay * 1.5, 30000);
        } else {
            console.error('최대 재연결 시도 횟수 초과');
        }
    }
    
    // WebSocket 메시지 처리
    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'status_update':
                this.updateSystemStatus(data.data);
                break;
            case 'test_update':
                this.updateTestResults(data.data);
                break;
            case 'workflow_progress':
                this.updateWorkflowProgress(data.data);
                break;
            default:
                console.log('알 수 없는 WebSocket 메시지:', data);
        }
    }
    
    // 연결 상태 업데이트
    updateConnectionStatus(connected) {
        const indicator = document.getElementById('ConnectionStatus');
        const statusText = document.getElementById('StatusText');
        
        if (indicator && statusText) {
            if (connected) {
                indicator.className = 'status-indicator status-online';
                statusText.textContent = '연결됨';
            } else {
                indicator.className = 'status-indicator status-offline';
                statusText.textContent = '연결 끊김';
            }
        }
    }
    
    // 시스템 상태 로드
    async loadSystemStatus() {
        try {
            const response = await fetch('/api/system/status');
            const status = await response.json();
            this.updateSystemStatus(status);
        } catch (error) {
            console.error('시스템 상태 로드 실패:', error);
        }
    }
    
    // 시스템 상태 업데이트
    updateSystemStatus(status) {
        // 전역 함수 호출 (각 페이지에서 구현)
        if (typeof updateSystemStatus === 'function') {
            updateSystemStatus(status);
        }
        
        // 대시보드 페이지의 상태 업데이트
        this.updateDashboardStatus(status);
    }
    
    // 대시보드 상태 업데이트
    updateDashboardStatus(status) {
        // LLM 상태
        const llmIndicator = document.getElementById('LlmStatus');
        const llmText = document.getElementById('LlmStatusText');
        if (llmIndicator && llmText) {
            if (status.llm_connected) {
                llmIndicator.className = 'status-indicator status-online';
                llmText.textContent = '연결됨';
            } else {
                llmIndicator.className = 'status-indicator status-offline';
                llmText.textContent = '연결 끊김';
            }
        }
        
        // Vector DB 상태
        const vectorIndicator = document.getElementById('VectorDbStatus');
        const vectorText = document.getElementById('VectorDbStatusText');
        if (vectorIndicator && vectorText) {
            if (status.vector_db_ready) {
                vectorIndicator.className = 'status-indicator status-online';
                vectorText.textContent = '준비됨';
            } else {
                vectorIndicator.className = 'status-indicator status-offline';
                vectorText.textContent = '연결 끊김';
            }
        }
        
        // 총 테스트 수
        const totalTestsCount = document.getElementById('TotalTestsCount');
        if (totalTestsCount) {
            totalTestsCount.textContent = status.total_tests || 0;
        }
        
        // 마지막 테스트 시간
        const lastTestTime = document.getElementById('LastTestTime');
        if (lastTestTime && status.last_test) {
            const date = new Date(status.last_test);
            lastTestTime.textContent = date.toLocaleString();
        }
    }
    
    // 테스트 결과 업데이트
    updateTestResults(testData) {
        // 전역 함수 호출 (각 페이지에서 구현)
        if (typeof updateTestResults === 'function') {
            updateTestResults(testData);
        }
    }
    
    // 워크플로우 진행상황 업데이트
    updateWorkflowProgress(progressData) {
        // 전역 함수 호출 (워크플로우 페이지에서 구현)
        if (typeof updateWorkflowProgress === 'function') {
            updateWorkflowProgress(progressData);
        }
    }
}

// 유틸리티 함수들
const Utils = {
    // 시간 포맷팅
    formatTime: (seconds) => {
        if (seconds < 1) {
            return `${(seconds * 1000).toFixed(0)}ms`;
        } else if (seconds < 60) {
            return `${seconds.toFixed(2)}초`;
        } else {
            const minutes = Math.floor(seconds / 60);
            const remainingSeconds = seconds % 60;
            return `${minutes}분 ${remainingSeconds.toFixed(1)}초`;
        }
    },
    
    // 숫자 포맷팅
    formatNumber: (num, decimals = 2) => {
        if (typeof num !== 'number') return num;
        return num.toFixed(decimals);
    },
    
    // 파일 크기 포맷팅
    formatFileSize: (bytes) => {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },
    
    // 날짜 포맷팅
    formatDateTime: (dateString) => {
        const date = new Date(dateString);
        return date.toLocaleString('ko-KR', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    },
    
    // 상대 시간 포맷팅
    formatRelativeTime: (dateString) => {
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now - date;
        const diffSecs = Math.floor(diffMs / 1000);
        const diffMins = Math.floor(diffSecs / 60);
        const diffHours = Math.floor(diffMins / 60);
        const diffDays = Math.floor(diffHours / 24);
        
        if (diffSecs < 60) {
            return `${diffSecs}초 전`;
        } else if (diffMins < 60) {
            return `${diffMins}분 전`;
        } else if (diffHours < 24) {
            return `${diffHours}시간 전`;
        } else {
            return `${diffDays}일 전`;
        }
    },
    
    // 에러 메시지 표시
    showError: (message, container = null) => {
        const alertHtml = `
            <div class="alert alert-danger alert-dismissible fade show" role="alert">
                <strong>오류:</strong> ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        if (container) {
            container.insertAdjacentHTML('afterbegin', alertHtml);
        } else {
            document.body.insertAdjacentHTML('afterbegin', alertHtml);
        }
        
        // 5초 후 자동 제거
        setTimeout(() => {
            const alert = document.querySelector('.alert-danger');
            if (alert) {
                alert.remove();
            }
        }, 5000);
    },
    
    // 성공 메시지 표시
    showSuccess: (message, container = null) => {
        const alertHtml = `
            <div class="alert alert-success alert-dismissible fade show" role="alert">
                <strong>성공:</strong> ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        if (container) {
            container.insertAdjacentHTML('afterbegin', alertHtml);
        } else {
            document.body.insertAdjacentHTML('afterbegin', alertHtml);
        }
        
        // 3초 후 자동 제거
        setTimeout(() => {
            const alert = document.querySelector('.alert-success');
            if (alert) {
                alert.remove();
            }
        }, 3000);
    },
    
    // 로딩 상태 토글
    toggleLoading: (element, loading = null) => {
        if (loading === null) {
            loading = !element.classList.contains('loading');
        }
        
        if (loading) {
            element.classList.add('loading');
            element.disabled = true;
            const originalText = element.textContent;
            element.dataset.originalText = originalText;
            element.innerHTML = '<span class="loading-spinner"></span> 처리 중...';
        } else {
            element.classList.remove('loading');
            element.disabled = false;
            if (element.dataset.originalText) {
                element.textContent = element.dataset.originalText;
                delete element.dataset.originalText;
            }
        }
    },
    
    // 디바운스 함수
    debounce: (func, wait, immediate) => {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                timeout = null;
                if (!immediate) func(...args);
            };
            const callNow = immediate && !timeout;
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
            if (callNow) func(...args);
        };
    },
    
    // 쓰로틀 함수
    throttle: (func, limit) => {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },
    
    // API 요청 래퍼
    api: {
        get: async (url) => {
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        },
        
        post: async (url, data) => {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        }
    }
};

// 전역 인스턴스 생성
let procureMateGUI;

// DOM 로드 완료시 초기화
document.addEventListener('DOMContentLoaded', () => {
    procureMateGUI = new ProcureMateGUI();
    
    // 툴팁 초기화 (Bootstrap)
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    
    // 페이지별 초기화
    const currentPage = window.location.pathname;
    if (currentPage.includes('llm-test')) {
        initLLMTestPage();
    } else if (currentPage.includes('rag-analysis')) {
        initRAGAnalysisPage();
    } else if (currentPage.includes('workflow')) {
        initWorkflowPage();
    } else {
        initDashboardPage();
    }
});

// 페이지별 초기화 함수들 (각 페이지에서 구현)
function initDashboardPage() {
    console.log('대시보드 페이지 초기화');
}

function initLLMTestPage() {
    console.log('LLM 테스트 페이지 초기화');
}

function initRAGAnalysisPage() {
    console.log('RAG 분석 페이지 초기화');
}

function initWorkflowPage() {
    console.log('워크플로우 페이지 초기화');
}

// 전역 함수로 내보내기
window.ProcureMateGUI = ProcureMateGUI;
window.Utils = Utils;
