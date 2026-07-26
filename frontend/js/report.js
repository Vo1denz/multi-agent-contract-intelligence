/**
 * ClauseIQ Risk Scorecard & Redline Suggestion Renderer
 */

class RiskReportRenderer {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
    }

    renderClauses(clauses) {
        if (!this.container) return;
        this.container.innerHTML = '';

        clauses.forEach(clause => {
            const card = document.createElement('div');
            card.className = 'clause-card';

            const badgeClass = clause.riskLevel === 'HIGH' ? 'badge-high' :
                               clause.riskLevel === 'MEDIUM' ? 'badge-signature' : 'badge-body';

            card.innerHTML = `
                <div class="clause-card-header">
                    <span class="clause-category">${clause.category}</span>
                    <span class="badge ${badgeClass}">${clause.riskLevel} RISK</span>
                </div>
                <p style="font-size: 0.85rem; color: #cbd5e1; margin-bottom: 0.5rem;">
                    "${clause.snippet}"
                </p>
                <div class="redline-suggestion">
                    <strong>Redline Suggestion:</strong> ${clause.redline}
                </div>
            `;

            this.container.appendChild(card);
        });
    }
}

window.RiskReportRenderer = RiskReportRenderer;
