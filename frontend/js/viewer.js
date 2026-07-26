/**
 * ClauseIQ Document Viewer & Bounding Box Overlay Canvas
 */

class DocumentViewer {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas ? this.canvas.getContext('2d') : null;
        this.showBoxes = true;
        this.scale = 1.0;
        this.currentBoxes = [];
        this.initListeners();
    }

    initListeners() {
        const toggleBtn = document.getElementById('btn-toggle-boxes');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => {
                this.showBoxes = !this.showBoxes;
                toggleBtn.classList.toggle('active', this.showBoxes);
                this.render();
            });
        }

        const zoomInBtn = document.getElementById('btn-zoom-in');
        if (zoomInBtn) {
            zoomInBtn.addEventListener('click', () => {
                this.scale = Math.min(this.scale + 0.15, 2.5);
                this.render();
            });
        }

        const zoomOutBtn = document.getElementById('btn-zoom-out');
        if (zoomOutBtn) {
            zoomOutBtn.addEventListener('click', () => {
                this.scale = Math.max(this.scale - 0.15, 0.5);
                this.render();
            });
        }
    }

    loadPage(pageData) {
        this.currentBoxes = pageData.boxes || [];
        // For demonstration, draw a placeholder contract page background
        this.render();
    }

    render() {
        if (!this.ctx) return;
        const width = 600 * this.scale;
        const height = 800 * this.scale;
        this.canvas.width = width;
        this.canvas.height = height;

        // Draw Document Sheet Background
        this.ctx.fillStyle = '#1e293b';
        this.ctx.fillRect(0, 0, width, height);

        // Draw Header Line Placeholder
        this.ctx.fillStyle = '#475569';
        this.ctx.fillRect(40 * this.scale, 40 * this.scale, 200 * this.scale, 16 * this.scale);

        // Draw Text Lines Placeholders
        for (let i = 0; i < 15; i++) {
            this.ctx.fillStyle = '#334155';
            this.ctx.fillRect(40 * this.scale, (90 + i * 36) * this.scale, 520 * this.scale, 12 * this.scale);
        }

        // Draw Bounding Boxes if enabled
        if (this.showBoxes) {
            this.currentBoxes.forEach(box => {
                this.drawBoundingBox(box);
            });
        }
    }

    drawBoundingBox(box) {
        const [x, y, w, h] = box.coords.map(c => c * this.scale);
        this.ctx.strokeStyle = box.color || '#ef4444';
        this.ctx.lineWidth = 2;
        this.ctx.strokeRect(x, y, w, h);

        // Label Tag
        this.ctx.fillStyle = box.color || '#ef4444';
        this.ctx.font = `600 ${11 * this.scale}px Inter, sans-serif`;
        this.ctx.fillText(box.label, x + 4, y - 6);
    }
}

window.DocumentViewer = DocumentViewer;
