const AGENT_STEPS = [
    { id: 'vision', name: 'Document Vision', icon: '👁️' },
    { id: 'extract', name: 'Extraction', icon: '📄' },
    { id: 'classify', name: 'Classification', icon: '🏷️' },
    { id: 'verify', name: 'Verification', icon: '✅' },
    { id: 'rag', name: 'Playbook RAG', icon: '📚' },
    { id: 'score', name: 'Risk Scoring', icon: '⚖️' },
    { id: 'critic', name: 'Critic', icon: '🧠' }
];

class ClauseIQApp {
    constructor() {
        this.state = 'IDLE'; // IDLE, UPLOADING, ANALYZING, COMPLETE, ERROR
        this.contractId = null;
        this.ws = null;
        
        this.viewer = new DocumentViewer('doc-canvas');
        this.reportRenderer = new ReportRenderer();
        
        this.initDOM();
        this.bindEvents();
        this.renderPipelineBar();
        this.updateUI('IDLE');
    }

    initDOM() {
        this.els = {
            emptyState: document.getElementById('empty-state'),
            analysisState: document.getElementById('analysis-state'),
            errorState: document.getElementById('error-state'),
            dropZone: document.getElementById('drop-zone'),
            fileInput: document.getElementById('file-upload'),
            pipelineProgress: document.getElementById('pipeline-progress'),
            btnZoomIn: document.getElementById('btn-zoom-in'),
            btnZoomOut: document.getElementById('btn-zoom-out'),
            btnToggleBoxes: document.getElementById('btn-toggle-boxes'),
            zoomLevel: document.getElementById('zoom-level'),
            btnRetry: document.getElementById('btn-retry'),
            toastContainer: document.getElementById('toast-container'),
            clauseModal: document.getElementById('clause-modal'),
            btnCloseModal: document.getElementById('btn-close-modal')
        };
    }

    bindEvents() {
        // Drag & Drop
        this.els.dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            this.els.dropZone.classList.add('dragover');
        });
        this.els.dropZone.addEventListener('dragleave', () => {
            this.els.dropZone.classList.remove('dragover');
        });
        this.els.dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            this.els.dropZone.classList.remove('dragover');
            if (e.dataTransfer.files.length) {
                this.handleFileUpload(e.dataTransfer.files[0]);
            }
        });

        // File Input
        this.els.fileInput.addEventListener('change', (e) => {
            if (e.target.files.length) {
                this.handleFileUpload(e.target.files[0]);
            }
        });

        // Viewer Controls
        this.els.btnZoomIn.addEventListener('click', () => {
            const scale = this.viewer.zoomIn();
            this.els.zoomLevel.textContent = `${Math.round(scale * 100)}%`;
        });
        this.els.btnZoomOut.addEventListener('click', () => {
            const scale = this.viewer.zoomOut();
            this.els.zoomLevel.textContent = `${Math.round(scale * 100)}%`;
        });
        this.els.btnToggleBoxes.addEventListener('click', () => {
            this.viewer.toggleBoxes();
        });

        // Page Selection (Event Delegation)
        document.getElementById('page-list').addEventListener('click', (e) => {
            const item = e.target.closest('.page-item');
            if (item) {
                document.querySelectorAll('.page-item').forEach(el => el.classList.remove('active'));
                item.classList.add('active');
                const pageNum = parseInt(item.dataset.page);
                this.viewer.showPage(pageNum);
            }
        });

        // Clause Click (Event Delegation)
        document.getElementById('clause-list').addEventListener('click', (e) => {
            const card = e.target.closest('.clause-card');
            if (card && window._currentClauses) {
                const index = parseInt(card.dataset.index);
                const clause = window._currentClauses[index];
                if (clause) {
                    this.reportRenderer.showClauseModal(clause);
                }
            }
        });

        // Modal Close
        this.els.btnCloseModal.addEventListener('click', () => {
            this.els.clauseModal.classList.remove('active');
        });
        this.els.clauseModal.addEventListener('click', (e) => {
            if (e.target === this.els.clauseModal) {
                this.els.clauseModal.classList.remove('active');
            }
        });

        // Retry
        this.els.btnRetry.addEventListener('click', () => {
            this.updateUI('IDLE');
        });
    }

    renderPipelineBar() {
        let html = '';
        AGENT_STEPS.forEach((step, index) => {
            html += `
                <div class="progress-step" id="step-${step.id}">
                    <div class="step-icon">${step.icon}</div>
                    <span class="step-label">${step.name}</span>
                </div>
            `;
            if (index < AGENT_STEPS.length - 1) {
                html += `<div class="step-connector"></div>`;
            }
        });
        this.els.pipelineProgress.innerHTML = html;
    }

    updatePipelineStatus(activeStepId) {
        let foundActive = false;
        AGENT_STEPS.forEach(step => {
            const el = document.getElementById(`step-${step.id}`);
            if (!el) return;
            
            el.classList.remove('active', 'done');
            
            if (step.id === activeStepId) {
                el.classList.add('active');
                foundActive = true;
            } else if (!foundActive && activeStepId !== null) {
                el.classList.add('done');
            }
        });
    }

    updateUI(state) {
        this.state = state;
        this.els.emptyState.classList.remove('active');
        this.els.analysisState.classList.remove('active');
        this.els.errorState.classList.remove('active');

        switch(state) {
            case 'IDLE':
                this.els.emptyState.classList.add('active');
                this.reportRenderer.clear();
                this.updatePipelineStatus(null);
                break;
            case 'UPLOADING':
                this.els.emptyState.classList.add('active');
                this.els.dropZone.innerHTML = '<div class="spinner" style="margin:0 auto;"></div><h3 style="margin-top:20px;">Uploading...</h3>';
                break;
            case 'ANALYZING':
                this.els.analysisState.classList.add('active');
                this.viewer.setLoading(true);
                break;
            case 'COMPLETE':
                this.els.analysisState.classList.add('active');
                this.viewer.setLoading(false);
                this.updatePipelineStatus(null); // all done
                document.querySelectorAll('.progress-step').forEach(el => el.classList.add('done'));
                this.showToast('Analysis complete!', 'success');
                break;
            case 'ERROR':
                this.els.errorState.classList.add('active');
                break;
        }
    }

    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        let color = 'var(--accent-blue)';
        if (type === 'success') color = 'var(--risk-low)';
        if (type === 'error') color = 'var(--risk-high)';
        
        toast.innerHTML = `
            <div style="font-weight: 600; color: hsl(${color}); margin-bottom: 4px;">ClauseIQ System</div>
            <div style="font-size: 0.9rem;">${message}</div>
        `;
        
        this.els.toastContainer.appendChild(toast);
        
        // Trigger reflow to enable transition
        void toast.offsetWidth;
        toast.classList.add('show');
        
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 5000);
    }

    async handleFileUpload(file) {
        this.updateUI('UPLOADING');
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/api/v1/contracts/upload', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) throw new Error('Upload failed');
            
            const data = await response.json();
            this.contractId = data.contract_id;
            
            this.startAnalysis(this.contractId);
            
        } catch (error) {
            console.error(error);
            document.getElementById('error-message').textContent = 'Failed to upload contract. Ensure backend is running.';
            this.updateUI('ERROR');
        }
    }

    startAnalysis(contractId) {
        this.updateUI('ANALYZING');
        
        // Setup WebSocket
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        // In local dev without correct port, we might fail, but let's assume standard behavior
        const host = window.location.host || 'localhost:8000';
        const wsUrl = `${protocol}//${host}/ws/analysis/${contractId}`;
        
        try {
            this.ws = new WebSocket(wsUrl);
            this.ws.onmessage = (e) => {
                const data = JSON.parse(e.data);
                this.handleAgentProgress(data);
            };
            this.ws.onerror = (e) => {
                console.warn('WebSocket error (ignoring if fallback to REST works)', e);
            };
        } catch(e) {
            console.warn('Could not connect WS, proceeding with REST only', e);
        }

        // Trigger Analysis POST
        fetch(`/api/v1/contracts/${contractId}/analyze`, { method: 'POST' })
            .then(res => res.json())
            .then(report => {
                this.handleAnalysisComplete(report);
            })
            .catch(err => {
                console.error(err);
                document.getElementById('error-message').textContent = 'Analysis pipeline failed. Check backend logs.';
                this.updateUI('ERROR');
            });
    }

    handleAgentProgress(msg) {
        // Map agent_name to step ID if possible
        const nameLower = (msg.agent_name || '').toLowerCase();
        let activeStep = null;
        if (nameLower.includes('vision')) activeStep = 'vision';
        else if (nameLower.includes('extract')) activeStep = 'extract';
        else if (nameLower.includes('classif')) activeStep = 'classify';
        else if (nameLower.includes('verif')) activeStep = 'verify';
        else if (nameLower.includes('rag')) activeStep = 'rag';
        else if (nameLower.includes('score')) activeStep = 'score';
        else if (nameLower.includes('critic')) activeStep = 'critic';

        if (activeStep) {
            this.updatePipelineStatus(activeStep);
        }
        
        if (msg.message) {
            this.showToast(`${msg.agent_name}: ${msg.message}`);
        }
    }

    handleAnalysisComplete(report) {
        if (this.ws) {
            this.ws.close();
        }
        this.reportRenderer.renderReport(report);
        this.viewer.loadPages(report.pages || []);
        this.updateUI('COMPLETE');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.app = new ClauseIQApp();
});
