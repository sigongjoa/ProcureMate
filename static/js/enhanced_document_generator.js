// Enhanced Document Generator - 템플릿 기능이 포함된 문서 생성기
class EnhancedDocumentGenerator {
    constructor() {
        this.selectedDocumentType = null;
        this.documentTypes = [];
        this.currentFormData = {};
        this.templates = {};
        this.init();
    }

    async init() {
        await this.loadDocumentTypes();
        await this.loadTemplates();
        this.setupEventListeners();
        console.log('EnhancedDocumentGenerator initialized');
    }

    async loadDocumentTypes() {
        try {
            const response = await fetch('/api/documents/types');
            const result = await response.json();
            
            if (result.success) {
                this.documentTypes = result.data;
                this.renderDocumentTypeList();
            } else {
                this.showError('문서 타입 로딩 실패');
            }
        } catch (error) {
            console.error('Document types load failed:', error);
            this.showError('서버 연결 오류');
        }
    }

    async loadTemplates() {
        try {
            const response = await fetch('/api/templates/document-list');
            const result = await response.json();
            
            if (result.success) {
                this.templates = result.data;
                this.renderTemplateSelector();
            }
        } catch (error) {
            console.error('Templates load failed:', error);
        }
    }

    renderTemplateSelector() {
        const selector = document.getElementById('TemplateSelector');
        const templateNames = Object.keys(this.templates);
        
        selector.innerHTML = '<option value="">템플릿을 선택하세요</option>' + 
            templateNames.map(name => `<option value="${name}">${name}</option>`).join('');
    }

    renderDocumentTypeList() {
        const container = document.getElementById('DocumentTypeList');
        
        if (this.documentTypes.length === 0) {
            container.innerHTML = '<div class="text-slate-500 dark:text-slate-400 text-center">사용 가능한 문서 타입이 없습니다</div>';
            return;
        }

        const listItems = this.documentTypes.map(type => `
            <button class="DocumentTypeItem w-full text-left p-4 border border-slate-200 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 hover:bg-slate-50 dark:hover:bg-slate-600 transition-colors duration-200" 
                    data-type="${type.id}">
                <div class="flex justify-between items-start mb-2">
                    <h4 class="font-medium text-slate-900 dark:text-slate-100">${type.name}</h4>
                    <span class="text-xs px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded-full">${type.category}</span>
                </div>
                <p class="text-sm text-slate-600 dark:text-slate-400">${type.description}</p>
            </button>
        `).join('');

        container.innerHTML = listItems;
    }

    setupEventListeners() {
        // 문서 타입 선택
        document.addEventListener('click', (e) => {
            if (e.target.closest('.DocumentTypeItem')) {
                const button = e.target.closest('.DocumentTypeItem');
                const documentType = button.dataset.type;
                this.selectDocumentType(documentType);
            }
        });

        // 문서 생성 버튼
        document.getElementById('GenerateButton').addEventListener('click', () => {
            this.generateDocument();
        });

        // 복사 버튼
        document.getElementById('CopyButton').addEventListener('click', () => {
            this.copyToClipboard();
        });

        // 다운로드 버튼
        document.getElementById('DownloadButton').addEventListener('click', () => {
            this.downloadDocument();
        });
    }

    async selectDocumentType(documentType) {
        // 이전 선택 제거
        document.querySelectorAll('.DocumentTypeItem').forEach(item => {
            item.classList.remove('ring-2', 'ring-primary-500', 'bg-primary-50', 'dark:bg-primary-900/20');
        });

        // 새 선택 적용
        const selectedItem = document.querySelector(`[data-type="${documentType}"]`);
        selectedItem.classList.add('ring-2', 'ring-primary-500', 'bg-primary-50', 'dark:bg-primary-900/20');
        
        this.selectedDocumentType = documentType;

        // 폼 필드 로딩
        await this.loadFormFields(documentType);
    }

    async loadFormFields(documentType) {
        try {
            const response = await fetch(`/api/documents/${documentType}/fields`);
            const result = await response.json();
            
            if (result.success) {
                this.renderFormFields(result.data);
                document.getElementById('GenerateButton').disabled = false;
            } else {
                this.showError('폼 필드 로딩 실패');
            }
        } catch (error) {
            console.error('Form fields load failed:', error);
            this.showError('서버 연결 오류');
        }
    }

    renderFormFields(fields) {
        const container = document.getElementById('DocumentFormContainer');
        
        const formHTML = fields.map(field => {
            const fieldId = `field_${field.name}`;
            const required = field.required ? 'required' : '';
            const placeholder = field.placeholder ? `placeholder="${field.placeholder}"` : '';
            const baseClasses = 'FormField w-full px-4 py-3 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-slate-100 placeholder-slate-500 dark:placeholder-slate-400 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200';

            switch (field.field_type) {
                case 'textarea':
                    return `
                        <div class="mb-6">
                            <label for="${fieldId}" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                                ${field.label} ${field.required ? '<span class="text-red-500">*</span>' : ''}
                            </label>
                            <textarea class="${baseClasses}" 
                                      id="${fieldId}" 
                                      name="${field.name}"
                                      rows="3" 
                                      ${placeholder} 
                                      ${required}></textarea>
                        </div>
                    `;
                case 'select':
                    const options = field.options ? field.options.map(opt => 
                        `<option value="${opt}">${opt}</option>`
                    ).join('') : '';
                    return `
                        <div class="mb-6">
                            <label for="${fieldId}" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                                ${field.label} ${field.required ? '<span class="text-red-500">*</span>' : ''}
                            </label>
                            <select class="${baseClasses}" 
                                    id="${fieldId}" 
                                    name="${field.name}" 
                                    ${required}>
                                <option value="">선택해주세요</option>
                                ${options}
                            </select>
                        </div>
                    `;
                case 'number':
                    return `
                        <div class="mb-6">
                            <label for="${fieldId}" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                                ${field.label} ${field.required ? '<span class="text-red-500">*</span>' : ''}
                            </label>
                            <input type="number" 
                                   class="${baseClasses}" 
                                   id="${fieldId}" 
                                   name="${field.name}"
                                   ${placeholder} 
                                   ${required}>
                        </div>
                    `;
                case 'date':
                    return `
                        <div class="mb-6">
                            <label for="${fieldId}" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                                ${field.label} ${field.required ? '<span class="text-red-500">*</span>' : ''}
                            </label>
                            <input type="date" 
                                   class="${baseClasses}" 
                                   id="${fieldId}" 
                                   name="${field.name}"
                                   ${required}>
                        </div>
                    `;
                default: // text
                    return `
                        <div class="mb-6">
                            <label for="${fieldId}" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                                ${field.label} ${field.required ? '<span class="text-red-500">*</span>' : ''}
                            </label>
                            <input type="text" 
                                   class="${baseClasses}" 
                                   id="${fieldId}" 
                                   name="${field.name}"
                                   ${placeholder} 
                                   ${required}>
                        </div>
                    `;
            }
        }).join('');

        container.innerHTML = `
            <form id="DocumentForm" class="space-y-6">
                ${formHTML}
            </form>
        `;
    }

    collectFormData() {
        const formData = {};
        document.querySelectorAll('.FormField').forEach(field => {
            const value = field.value.trim();
            if (value) {
                if (field.type === 'number') {
                    formData[field.name] = parseFloat(value);
                } else {
                    formData[field.name] = value;
                }
            }
        });
        return formData;
    }

    async generateDocument() {
        if (!this.selectedDocumentType) {
            this.showError('문서 타입을 선택해주세요');
            return;
        }

        const formData = this.collectFormData();
        
        // 진행 모달 표시
        this.showProgressModal();

        try {
            const response = await fetch('/api/documents/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    document_type: this.selectedDocumentType,
                    form_data: formData
                })
            });

            const result = await response.json();
            this.hideProgressModal();

            if (result.success) {
                this.displayGeneratedDocument(result.data);
            } else {
                this.showError('문서 생성 실패: ' + (result.error || '알 수 없는 오류'));
            }
        } catch (error) {
            this.hideProgressModal();
            console.error('Document generation failed:', error);
            this.showError('서버 연결 오류');
        }
    }

    displayGeneratedDocument(documentData) {
        const content = documentData.generated_content || '생성된 내용이 없습니다';
        
        // 마크다운을 HTML로 변환
        const htmlContent = this.markdownToHtml(content);
        
        document.getElementById('GeneratedContent').innerHTML = `
            <div class="generated-document prose dark:prose-invert max-w-none">
                ${htmlContent}
            </div>
            <div class="mt-6 pt-6 border-t border-slate-200 dark:border-slate-600">
                <h4 class="font-semibold text-slate-900 dark:text-slate-100 mb-3">문서 정보</h4>
                <div class="grid grid-cols-2 gap-4 text-sm">
                    <div>
                        <span class="font-medium text-slate-700 dark:text-slate-300">문서 타입:</span>
                        <span class="text-slate-600 dark:text-slate-400 ml-2">${documentData.template_name}</span>
                    </div>
                    <div>
                        <span class="font-medium text-slate-700 dark:text-slate-300">생성 시간:</span>
                        <span class="text-slate-600 dark:text-slate-400 ml-2">${new Date(documentData.timestamp).toLocaleString('ko-KR')}</span>
                    </div>
                </div>
            </div>
        `;

        // 결과 섹션 표시
        document.getElementById('ResultSection').classList.remove('hidden');
        document.getElementById('ResultSection').scrollIntoView({ behavior: 'smooth' });

        this.currentFormData = documentData;
    }

    markdownToHtml(markdown) {
        return markdown
            .replace(/^# (.*$)/gm, '<h1 class="text-2xl font-bold mb-4">$1</h1>')
            .replace(/^## (.*$)/gm, '<h2 class="text-xl font-semibold mb-3">$1</h2>')
            .replace(/^### (.*$)/gm, '<h3 class="text-lg font-medium mb-2">$1</h3>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/^\* (.*$)/gm, '<li>$1</li>')
            .replace(/^- (.*$)/gm, '<li>$1</li>')
            .replace(/\n\n/g, '</p><p class="mb-4">')
            .replace(/^(.+)$/gm, '<p class="mb-4">$1</p>')
            .replace(/<p class="mb-4"><li>/g, '<ul class="list-disc pl-6 mb-4"><li>')
            .replace(/<\/li><\/p>/g, '</li></ul>');
    }

    copyToClipboard() {
        const content = document.getElementById('GeneratedContent').innerText;
        navigator.clipboard.writeText(content).then(() => {
            const button = document.getElementById('CopyButton');
            const originalHTML = button.innerHTML;
            
            button.innerHTML = `
                <svg class="w-4 h-4 inline-block mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
                복사됨
            `;
            button.classList.remove('border-slate-300', 'dark:border-slate-600', 'text-slate-700', 'dark:text-slate-300');
            button.classList.add('border-emerald-500', 'text-emerald-600', 'bg-emerald-50', 'dark:bg-emerald-900/20');
            
            setTimeout(() => {
                button.innerHTML = originalHTML;
                button.classList.add('border-slate-300', 'dark:border-slate-600', 'text-slate-700', 'dark:text-slate-300');
                button.classList.remove('border-emerald-500', 'text-emerald-600', 'bg-emerald-50', 'dark:bg-emerald-900/20');
            }, 2000);
        });
    }

    downloadDocument() {
        if (!this.currentFormData) return;
        
        const content = this.currentFormData.generated_content || '';
        const filename = `${this.selectedDocumentType}_${new Date().toISOString().slice(0,10)}.txt`;
        
        const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    }

    showProgressModal() {
        document.getElementById('ProgressModal').classList.remove('hidden');
        
        // 진행률 애니메이션
        let progress = 0;
        const progressBar = document.getElementById('ProgressBar');
        const interval = setInterval(() => {
            progress += Math.random() * 20;
            if (progress > 90) progress = 90;
            progressBar.style.width = `${progress}%`;
        }, 500);
        
        this.progressInterval = interval;
    }

    hideProgressModal() {
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
        }
        
        // 완료 애니메이션
        document.getElementById('ProgressBar').style.width = '100%';
        
        setTimeout(() => {
            document.getElementById('ProgressModal').classList.add('hidden');
            document.getElementById('ProgressBar').style.width = '0%';
        }, 500);
    }

    showError(message) {
        const alertDiv = document.createElement('div');
        alertDiv.className = 'fixed top-4 right-4 bg-red-500 text-white px-6 py-4 rounded-lg shadow-lg z-50 transform translate-x-full transition-transform duration-300';
        alertDiv.innerHTML = `
            <div class="flex items-center justify-between">
                <span>${message}</span>
                <button onclick="this.closest('div').remove()" class="ml-4 text-white hover:text-red-200">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                </button>
            </div>
        `;
        
        document.body.appendChild(alertDiv);
        
        // 애니메이션
        setTimeout(() => {
            alertDiv.classList.remove('translate-x-full');
        }, 100);
        
        // 자동 제거
        setTimeout(() => {
            alertDiv.classList.add('translate-x-full');
            setTimeout(() => {
                if (alertDiv.parentNode) {
                    alertDiv.remove();
                }
            }, 300);
        }, 5000);
    }

    // 템플릿 관련 메서드들
    loadSelectedTemplate() {
        const selectedTemplate = document.getElementById('TemplateSelector').value;
        if (!selectedTemplate) {
            this.showError('템플릿을 선택하세요');
            return;
        }

        const template = this.templates[selectedTemplate];
        if (template) {
            // 문서 타입 설정
            if (template.document_type) {
                this.selectDocumentType(template.document_type);
            }

            // 폼 데이터 설정
            setTimeout(() => {
                this.populateFormWithTemplate(template.form_data);
            }, 100);

            this.showNotification(`템플릿 '${selectedTemplate}'을 불러왔습니다`, 'success');
        }
    }

    populateFormWithTemplate(formData) {
        Object.keys(formData).forEach(fieldName => {
            const field = document.querySelector(`[name="${fieldName}"]`);
            if (field) {
                field.value = formData[fieldName];
            }
        });
    }

    saveCurrentAsTemplate() {
        const templateName = document.getElementById('NewTemplateName').value.trim();
        
        if (!templateName) {
            this.showError('템플릿 이름을 입력하세요');
            return;
        }

        if (!this.selectedDocumentType) {
            this.showError('문서 타입을 선택하세요');
            return;
        }

        // 템플릿 저장 모달 표시
        document.getElementById('SaveTemplateName').value = templateName;
        document.getElementById('TemplateSaveModal').classList.remove('hidden');
    }

    async confirmSaveTemplate() {
        const name = document.getElementById('SaveTemplateName').value.trim();
        const description = document.getElementById('SaveTemplateDesc').value.trim();
        
        if (!name) {
            this.showError('템플릿 이름을 입력하세요');
            return;
        }

        const templateData = {
            name,
            description,
            document_type: this.selectedDocumentType,
            form_data: this.collectFormData(),
            created_at: new Date().toISOString()
        };

        try {
            const response = await fetch('/api/templates/document-save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(templateData)
            });

            const result = await response.json();
            
            if (result.success) {
                this.templates[name] = templateData;
                this.renderTemplateSelector();
                this.showNotification('템플릿이 저장되었습니다', 'success');
                this.closeSaveModal();
                
                // 입력 필드 초기화
                document.getElementById('NewTemplateName').value = '';
            } else {
                this.showError('템플릿 저장 실패');
            }
        } catch (error) {
            console.error('Template save failed:', error);
            this.showError('서버 연결 오류');
        }
    }

    closeSaveModal() {
        document.getElementById('TemplateSaveModal').classList.add('hidden');
    }

    showNotification(message, type = 'info') {
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
}

// 전역 함수들
function loadSelectedTemplate() {
    window.documentGenerator.loadSelectedTemplate();
}

function saveCurrentAsTemplate() {
    window.documentGenerator.saveCurrentAsTemplate();
}

function confirmSaveTemplate() {
    window.documentGenerator.confirmSaveTemplate();
}

function closeSaveModal() {
    window.documentGenerator.closeSaveModal();
}

// 시스템 상태 업데이트
function updateSystemStatus(status) {
    console.log('Enhanced document generator system status update:', status);
}

// 페이지 로드 시 초기화
document.addEventListener('DOMContentLoaded', function() {
    window.documentGenerator = new EnhancedDocumentGenerator();
});
