// Settings Page JavaScript - 네비게이션 기반 설정 관리
class SettingsManager {
    constructor() {
        this.currentTab = 'llm';
        this.settings = {};
        this.init();
    }

    init() {
        this.setupNavigation();
        this.setupEventListeners();
        this.loadSettings();
        console.log('SettingsManager initialized');
    }

    setupNavigation() {
        document.querySelectorAll('.NavMenuItem').forEach(item => {
            item.addEventListener('click', (e) => {
                const tabId = e.currentTarget.dataset.tab;
                this.switchTab(tabId);
            });
        });
    }

    switchTab(tabId) {
        // 네비게이션 상태 업데이트
        document.querySelectorAll('.NavMenuItem').forEach(item => {
            item.classList.remove('active', 'bg-primary-100', 'dark:bg-primary-900/20', 'text-primary-700', 'dark:text-primary-300');
        });
        document.querySelector(`[data-tab="${tabId}"]`).classList.add('active', 'bg-primary-100', 'dark:bg-primary-900/20', 'text-primary-700', 'dark:text-primary-300');

        // 탭 콘텐츠 전환
        document.querySelectorAll('.TabContent').forEach(content => {
            content.classList.add('hidden');
        });
        document.getElementById(`tab-${tabId}`).classList.remove('hidden');

        this.currentTab = tabId;
    }

    setupEventListeners() {
        // Temperature 슬라이더
        document.getElementById('LlmTemperature').addEventListener('input', (e) => {
            document.getElementById('TempDisplay').textContent = e.target.value;
        });
    }

    async loadSettings() {
        try {
            const response = await fetch('/api/settings/load');
            const result = await response.json();
            
            if (result.success) {
                this.settings = result.data;
                this.populateForm();
            }
        } catch (error) {
            console.error('Settings load failed:', error);
        }
    }

    populateForm() {
        const { llm, vectordb, apis, system } = this.settings;
        
        if (llm) {
            document.getElementById('LlmServerUrl').value = llm.server_url || '';
            document.getElementById('LlmModel').value = llm.model || '';
            document.getElementById('LlmTemperature').value = llm.default_temperature || 0.7;
            document.getElementById('TempDisplay').textContent = llm.default_temperature || 0.7;
            document.getElementById('LlmMaxTokens').value = llm.default_max_tokens || 1024;
        }
        
        if (vectordb) {
            document.getElementById('ChromaDbPath').value = vectordb.db_path || '';
            document.getElementById('CollectionName').value = vectordb.collection_name || '';
            document.getElementById('EmbeddingModel').value = vectordb.embedding_model || '';
        }
        
        if (apis) {
            document.getElementById('G2bApiKey').value = apis.g2b_api_key || '';
            document.getElementById('CoupangAccessKey').value = apis.coupang_access_key || '';
            document.getElementById('CoupangSecretKey').value = apis.coupang_secret_key || '';
        }
        
        if (system) {
            document.getElementById('DebugMode').checked = system.debug_mode || false;
            document.getElementById('AutoSave').checked = system.auto_save !== false;
        }
    }

    collectSettings() {
        return {
            llm: {
                server_url: document.getElementById('LlmServerUrl').value,
                model: document.getElementById('LlmModel').value,
                default_temperature: parseFloat(document.getElementById('LlmTemperature').value),
                default_max_tokens: parseInt(document.getElementById('LlmMaxTokens').value)
            },
            vectordb: {
                db_path: document.getElementById('ChromaDbPath').value,
                collection_name: document.getElementById('CollectionName').value,
                embedding_model: document.getElementById('EmbeddingModel').value
            },
            apis: {
                g2b_api_key: document.getElementById('G2bApiKey').value,
                coupang_access_key: document.getElementById('CoupangAccessKey').value,
                coupang_secret_key: document.getElementById('CoupangSecretKey').value
            },
            system: {
                debug_mode: document.getElementById('DebugMode').checked,
                auto_save: document.getElementById('AutoSave').checked
            }
        };
    }
}

// TemplateManager
class TemplateManager {
    constructor() {
        this.documentTemplates = [];
        this.settingTemplates = [];
        this.currentType = 'document';
        this.loadTemplates();
    }

    async loadTemplates() {
        try {
            // 문서 템플릿 로드
            const docResponse = await fetch('/api/templates/document/list');
            const docResult = await docResponse.json();
            
            if (docResult.success) {
                this.documentTemplates = docResult.templates;
            }
            
            // 설정 템플릿 로드
            const settingResponse = await fetch('/api/templates/setting/list');
            const settingResult = await settingResponse.json();
            
            if (settingResult.success) {
                this.settingTemplates = settingResult.templates;
            }
            
            this.renderTemplateList();
        } catch (error) {
            console.error('Template load failed:', error);
            showNotification('템플릿 로드 실패', 'error');
        }
    }

    renderTemplateList() {
        const container = document.getElementById('TemplateList');
        const templates = this.currentType === 'document' ? this.documentTemplates : this.settingTemplates;
        
        if (templates.length === 0) {
            container.innerHTML = '<p class="text-slate-500">저장된 템플릿이 없습니다</p>';
            return;
        }

        container.innerHTML = `
            <div class="mb-4">
                <label class="block text-sm font-medium mb-2">템플릿 타입</label>
                <select id="TemplateTypeSelect" class="w-full px-3 py-2 border rounded-lg" onchange="changeTemplateType(this.value)">
                    <option value="document" ${this.currentType === 'document' ? 'selected' : ''}>문서 템플릿</option>
                    <option value="setting" ${this.currentType === 'setting' ? 'selected' : ''}>설정 템플릿</option>
                </select>
            </div>
            ${templates.map(template => `
                <div class="TemplateItem flex items-center justify-between p-3 border border-slate-200 dark:border-slate-600 rounded-lg mb-2">
                    <div>
                        <span class="font-medium">${template.name}</span>
                        <div class="text-xs text-slate-500 mt-1">
                            수정: ${new Date(template.modified).toLocaleDateString()}
                        </div>
                    </div>
                    <div class="space-x-2">
                        <button onclick="loadTemplate('${template.name}')" class="text-blue-600 hover:text-blue-700 text-sm">불러오기</button>
                        <button onclick="deleteTemplate('${template.name}')" class="text-red-600 hover:text-red-700 text-sm">삭제</button>
                    </div>
                </div>
            `).join('')}
        `;
    }
    
    changeTemplateType(type) {
        this.currentType = type;
        this.renderTemplateList();
    }

    async saveTemplate() {
        const name = document.getElementById('TemplateName').value.trim();
        const content = document.getElementById('TemplateContent').value.trim();
        
        if (!name || !content) {
            showNotification('템플릿 이름과 내용을 입력하세요', 'error');
            return;
        }

        try {
            JSON.parse(content); // JSON 유효성 검사
            
            const response = await fetch('/api/templates/save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, content })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.templates[name] = JSON.parse(content);
                this.renderTemplateList();
                showNotification('템플릿이 저장되었습니다', 'success');
                
                // 입력 필드 초기화
                document.getElementById('TemplateName').value = '';
                document.getElementById('TemplateContent').value = '';
            }
        } catch (error) {
            console.error('Template save failed:', error);
            showNotification('JSON 형식이 올바르지 않습니다', 'error');
        }
    }

    loadTemplate(name) {
        const template = this.templates[name];
        if (template) {
            document.getElementById('TemplateContent').value = JSON.stringify(template, null, 2);
            showNotification(`템플릿 '${name}'이 로드되었습니다`, 'success');
        }
    }

    async deleteTemplate(name) {
        if (confirm(`템플릿 '${name}'을 삭제하시겠습니까?`)) {
            try {
                const response = await fetch(`/api/templates/delete/${name}`, { method: 'DELETE' });
                const result = await response.json();
                
                if (result.success) {
                    delete this.templates[name];
                    this.renderTemplateList();
                    showNotification('템플릿이 삭제되었습니다', 'success');
                }
            } catch (error) {
                console.error('Template delete failed:', error);
            }
        }
    }
}

// 전역 함수들
async function testLLM() {
    showLoading('LLM 연결 테스트 중...');
    try {
        const response = await fetch('/api/llm/test-connection', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                server_url: document.getElementById('LlmServerUrl').value,
                model: document.getElementById('LlmModel').value
            })
        });
        
        const result = await response.json();
        hideLoading();
        
        showNotification(result.success ? 'LLM 연결 성공!' : 'LLM 연결 실패', result.success ? 'success' : 'error');
    } catch (error) {
        hideLoading();
        console.error('LLM test failed:', error);
    }
}

async function testVectorDB() {
    showLoading('Vector DB 테스트 중...');
    try {
        const response = await fetch('/api/vectordb/test-connection', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                db_path: document.getElementById('ChromaDbPath').value,
                collection_name: document.getElementById('CollectionName').value
            })
        });
        
        const result = await response.json();
        hideLoading();
        
        showNotification(result.success ? 'Vector DB 연결 성공!' : 'Vector DB 연결 실패', result.success ? 'success' : 'error');
    } catch (error) {
        hideLoading();
        console.error('VectorDB test failed:', error);
    }
}

async function testAPI() {
    showLoading('API 테스트 중...');
    try {
        const response = await fetch('/api/external/test-connections', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                g2b_api_key: document.getElementById('G2bApiKey').value,
                coupang_access_key: document.getElementById('CoupangAccessKey').value,
                coupang_secret_key: document.getElementById('CoupangSecretKey').value
            })
        });
        
        const result = await response.json();
        hideLoading();
        
        showNotification('API 테스트 완료', 'success');
    } catch (error) {
        hideLoading();
        console.error('API test failed:', error);
    }
}

function saveTemplate() {
    window.templateManager.saveTemplate();
}

function loadTemplate(name) {
    window.templateManager.loadTemplate(name);
}

function deleteTemplate(name) {
    window.templateManager.deleteTemplate(name);
}

function changeTemplateType(type) {
    window.templateManager.changeTemplateType(type);
}

// Notion 연동 기능
class NotionIntegration {
    constructor() {
        this.connected = false;
        this.testConnection();
    }
    
    async testConnection() {
        try {
            const response = await fetch('/api/notion/test');
            const result = await response.json();
            this.connected = result.success;
            
            if (!this.connected) {
                console.warn('Notion 연결 실패:', result.error);
            }
        } catch (error) {
            console.error('Notion 연결 테스트 오류:', error);
            this.connected = false;
        }
    }
    
    async logImplementationStatus(moduleName, status, progress = 0) {
        if (!this.connected) return;
        
        try {
            const response = await fetch('/api/notion/log/implementation', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    module_name: moduleName,
                    status: status,
                    progress: progress
                })
            });
            
            const result = await response.json();
            if (result.success) {
                console.log(`Notion 구현 상황 로깅 성공: ${moduleName}`);
            }
        } catch (error) {
            console.error('Notion 구현 로깅 실패:', error);
        }
    }
    
    async logDailyProgress(date, changes, nextSteps) {
        if (!this.connected) return;
        
        try {
            const response = await fetch('/api/notion/log/daily', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    date: date,
                    changes: changes,
                    next_steps: nextSteps
                })
            });
            
            const result = await response.json();
            if (result.success) {
                console.log(`Notion 일일 진행 로깅 성공: ${date}`);
            }
        } catch (error) {
            console.error('Notion 일일 로깅 실패:', error);
        }
    }
    
    async logIssue(title, description, priority = '중간') {
        if (!this.connected) return;
        
        try {
            const response = await fetch('/api/notion/log/issue', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    title: title,
                    description: description,
                    priority: priority
                })
            });
            
            const result = await response.json();
            if (result.success) {
                console.log(`Notion 이슈 로깅 성공: ${title}`);
            }
        } catch (error) {
            console.error('Notion 이슈 로깅 실패:', error);
        }
    }
}

function showLoading(text) {
    document.getElementById('LoadingText').textContent = text;
    document.getElementById('LoadingModal').classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('LoadingModal').classList.add('hidden');
}

function showNotification(message, type = 'info') {
    const colors = {
        success: 'bg-emerald-500',
        error: 'bg-red-500',
        warning: 'bg-yellow-500',
        info: 'bg-blue-500'
    };
    
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 ${colors[type]} text-white px-6 py-3 rounded-lg shadow-lg z-50 transform translate-x-full transition-transform duration-300`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => notification.classList.remove('translate-x-full'), 100);
    setTimeout(() => {
        notification.classList.add('translate-x-full');
        setTimeout(() => document.body.removeChild(notification), 300);
    }, 3000);
}

// 시스템 상태 업데이트
function updateSystemStatus(status) {
    console.log('Settings system status update:', status);
}

// 초기화
document.addEventListener('DOMContentLoaded', function() {
    window.settingsManager = new SettingsManager();
    window.templateManager = new TemplateManager();
    window.notionIntegration = new NotionIntegration();
    
    // Notion 로깅 - 설정 페이지 접속
    setTimeout(() => {
        if (window.notionIntegration.connected) {
            window.notionIntegration.logImplementationStatus(
                '설정 페이지',
                '접속',
                100
            );
        }
    }, 1000);
    
    console.log('Settings page initialized with enhanced features');
});
