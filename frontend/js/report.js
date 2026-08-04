class ReportRenderer {
    constructor() {
        this.gaugeContainer = document.getElementById('risk-gauge-container');
        this.summaryText = document.getElementById('risk-summary-text');
        this.pageList = document.getElementById('page-list');
        this.clauseList = document.getElementById('clause-list');
        this.auditTrail = document.getElementById('audit-trail');
        this.partiesList = document.getElementById('parties-list');
        this.executionStatus = document.getElementById('execution-status');
        this.modalBody = document.getElementById('modal-clause-body');
        this.modalCategory = document.getElementById('modal-clause-category');
        this.modalOverlay = document.getElementById('clause-modal');
    }

    renderReport(report) {
        this.renderRiskGauge(report.overall_risk_score || 0);
        this.summaryText.textContent = report.risk_summary || 'Analysis complete.';
        this.renderPageList(report.pages || []);
        this.renderParties(report.parties || []);
        this.renderExecutionStatus(report.vqa_issues || [], report.execution_complete);
        this.renderClauses(report.clauses || []);
        this.renderAuditTrail(report.audit_trail || []);
    }

    renderRiskGauge(score) {
        let color = '#22c55e'; // low
        if (score > 30) color = '#f59e0b'; // med
        if (score > 60) color = '#ef4444'; // high
        if (score > 80) color = '#a855f7'; // critical

        const strokeDasharray = 283; // 2 * pi * r (r=45)
        const strokeDashoffset = strokeDasharray - (strokeDasharray * score) / 100;

        this.gaugeContainer.innerHTML = `
            <svg viewBox="0 0 100 100" class="risk-gauge" style="width: 100%; height: 100%;">
                <circle cx="50" cy="50" r="45" fill="none" stroke="hsla(222, 47%, 30%, 0.5)" stroke-width="8"></circle>
                <circle cx="50" cy="50" r="45" fill="none" stroke="${color}" stroke-width="8" 
                    stroke-dasharray="${strokeDasharray}" 
                    stroke-dashoffset="${strokeDashoffset}" 
                    stroke-linecap="round" 
                    transform="rotate(-90 50 50)"
                    style="transition: stroke-dashoffset 1s ease-out;"></circle>
                <text x="50" y="55" font-family="Outfit" font-size="24" font-weight="700" fill="#fff" text-anchor="middle">${score}</text>
            </svg>
        `;
    }

    renderPageList(pages) {
        this.pageList.innerHTML = pages.map((p, i) => `
            <div class="page-item ${i === 0 ? 'active' : ''}" data-page="${p.page_number}">
                <span class="page-name">Page ${p.page_number}</span>
                <span class="badge badge-info">${p.page_type || 'UNKNOWN'}</span>
            </div>
        `).join('');
    }

    renderParties(parties) {
        if (parties.length === 0) {
            this.partiesList.innerHTML = '<span style="color: hsl(var(--text-muted)); font-size: 0.85rem;">None detected</span>';
            return;
        }
        this.partiesList.innerHTML = parties.map(p => `
            <div class="badge badge-info" style="margin-bottom: 4px; display: inline-block; margin-right: 4px;">${p}</div>
        `).join('');
    }

    renderExecutionStatus(vqaIssues, isComplete) {
        let html = '';
        if (isComplete !== undefined) {
            html += `<div style="margin-bottom: 8px; font-size: 0.85rem; color: ${isComplete ? '#22c55e' : '#f59e0b'}">
                Status: ${isComplete ? 'Fully Executed' : 'Execution Incomplete'}
            </div>`;
        }
        
        if (vqaIssues.length > 0) {
            html += vqaIssues.map(v => `
                <div style="background: hsla(222, 47%, 18%, 0.5); padding: 8px; border-radius: 6px; margin-bottom: 8px; font-size: 0.85rem;">
                    <strong>Q (Pg ${v.page_number}):</strong> ${v.question}<br/>
                    <strong style="color: ${v.is_complete ? '#22c55e' : '#ef4444'}">A:</strong> ${v.answer}
                </div>
            `).join('');
        }
        
        this.executionStatus.innerHTML = html || '<span style="color: hsl(var(--text-muted)); font-size: 0.85rem;">No execution issues</span>';
    }

    renderClauses(clauses) {
        if (clauses.length === 0) {
            this.clauseList.innerHTML = '<p style="color: hsl(var(--text-muted)); font-size: 0.85rem;">No critical clauses detected.</p>';
            return;
        }
        
        // Store clauses globally or attach to DOM for click handlers
        window._currentClauses = clauses;

        this.clauseList.innerHTML = clauses.map((c, i) => {
            const rLevel = c.risk_level ? c.risk_level.toLowerCase() : 'info';
            return `
            <div class="clause-card" data-index="${i}">
                <div class="clause-header">
                    <span style="font-weight: 600; font-size: 0.85rem;">${c.category}</span>
                    <span class="badge badge-${rLevel}">${c.risk_level}</span>
                </div>
                <div class="clause-preview">${c.text}</div>
            </div>
        `}).join('');
    }

    renderAuditTrail(trail) {
        this.auditTrail.innerHTML = trail.map(t => `
            <div style="margin-bottom: 12px; font-size: 0.85rem; padding-left: 12px; border-left: 2px solid hsl(var(--glass-border));">
                <span style="color: hsl(var(--accent-blue))">•</span> ${t}
            </div>
        `).join('');
    }

    showClauseModal(clause) {
        this.modalCategory.textContent = clause.category || 'Clause Detail';
        
        let entitiesHtml = '';
        if (clause.entities && clause.entities.length > 0) {
            entitiesHtml = `<div style="margin-top: 1rem;">
                <strong>Extracted Entities:</strong>
                <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-top: 4px;">
                    ${clause.entities.map(e => `<span class="badge badge-info">${e}</span>`).join('')}
                </div>
            </div>`;
        }

        this.modalBody.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <span class="badge badge-${(clause.risk_level||'info').toLowerCase()}">${clause.risk_level || 'INFO'} RISK</span>
                <span style="font-size: 0.85rem; color: hsl(var(--text-muted))">Confidence: ${Math.round((clause.confidence||0)*100)}%</span>
            </div>
            
            <div class="comparison-grid">
                <div class="comparison-box">
                    <h4>Detected Contract Text</h4>
                    <p style="color: hsl(var(--risk-high)); font-family: monospace; font-size: 0.85rem;">${clause.text || 'N/A'}</p>
                </div>
                <div class="comparison-box">
                    <h4>Playbook Precedent</h4>
                    <p style="color: hsl(var(--risk-low)); font-family: monospace; font-size: 0.85rem;">${clause.precedent_text || 'No precedent found'}</p>
                </div>
            </div>
            
            ${clause.redline_suggestion ? `
                <div class="comparison-box" style="margin-top: 1rem; border-color: hsl(var(--accent-blue));">
                    <h4 style="color: hsl(var(--accent-blue))">Redline Suggestion</h4>
                    <p style="font-family: monospace; font-size: 0.85rem;">${clause.redline_suggestion}</p>
                </div>
            ` : ''}
            
            ${entitiesHtml}
            
            ${clause.semantic_deviation !== undefined ? `
                <div style="margin-top: 1.5rem;">
                    <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 4px;">
                        <span>Semantic Deviation</span>
                        <span>${Math.round(clause.semantic_deviation * 100)}%</span>
                    </div>
                    <div style="height: 6px; background: hsla(var(--bg-dark), 0.5); border-radius: 3px; overflow: hidden;">
                        <div style="height: 100%; width: ${Math.round(clause.semantic_deviation * 100)}%; background: hsl(var(--risk-med));"></div>
                    </div>
                </div>
            ` : ''}
        `;
        
        this.modalOverlay.classList.add('active');
    }

    clear() {
        this.gaugeContainer.innerHTML = '';
        this.summaryText.textContent = '';
        this.pageList.innerHTML = '';
        this.clauseList.innerHTML = '';
        this.auditTrail.innerHTML = '';
        this.partiesList.innerHTML = '';
        this.executionStatus.innerHTML = '';
    }
}
