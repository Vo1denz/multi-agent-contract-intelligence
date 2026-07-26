/**
 * ClauseIQ Main Frontend Application Logic
 */

document.addEventListener('DOMContentLoaded', () => {
    const viewer = new window.DocumentViewer('document-canvas');
    const reporter = new window.RiskReportRenderer('clause-list');

    // Sample Contract Data Demonstration
    const samplePage2Data = {
        page: 2,
        boxes: [
            {
                coords: [40, 200, 520, 80],
                label: "Limitation of Liability (Clause 12.4)",
                color: "#ef4444"
            },
            {
                coords: [440, 160, 110, 32],
                label: "Handwritten Redline Contradiction",
                color: "#f59e0b"
            }
        ]
    };

    const sampleClauses = [
        {
            category: "Limitation of Liability",
            riskLevel: "HIGH",
            snippet: "Vendor's total liability shall not exceed 0.25x the total fees paid...",
            redline: "Replace '0.25x' with '2.0x total fees paid in the preceding 12 months' per playbook rule."
        },
        {
            category: "Indemnification",
            riskLevel: "HIGH",
            snippet: "Customer shall indemnify Vendor against all claims, including consequential losses...",
            redline: "Limit indemnification strictly to third-party IP infringement claims."
        },
        {
            category: "Governing Law",
            riskLevel: "MEDIUM",
            snippet: "This agreement shall be governed by the laws of the State of Texas.",
            redline: "Change jurisdiction to State of Delaware or State of New York."
        }
    ];

    // Initial Load
    viewer.loadPage(samplePage2Data);
    reporter.renderClauses(sampleClauses);

    // Page switcher events
    const pageItems = document.querySelectorAll('.page-item');
    pageItems.forEach(item => {
        item.addEventListener('click', () => {
            pageItems.forEach(p => p.classList.remove('active'));
            item.classList.add('active');
            const pageNum = parseInt(item.getAttribute('data-page') || '1', 10);

            if (pageNum === 2) {
                viewer.loadPage(samplePage2Data);
            } else {
                viewer.loadPage({ page: pageNum, boxes: [] });
            }
        });
    });

    // Sample button click
    const loadSampleBtn = document.getElementById('btn-sample-load');
    if (loadSampleBtn) {
        loadSampleBtn.addEventListener('click', () => {
            viewer.loadPage(samplePage2Data);
            reporter.renderClauses(sampleClauses);
            alert('Loaded ClauseIQ benchmark demo contract with handwritten redlines.');
        });
    }
});
