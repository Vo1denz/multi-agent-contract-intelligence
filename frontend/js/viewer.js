class DocumentViewer {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.pages = [];
        this.currentPage = null;
        this.scale = 1.0;
        this.showBoxes = true;
        this.currentImage = null;
        this.container = document.getElementById('canvas-container');
        
        window.addEventListener('resize', () => this.draw());
    }

    setLoading(isLoading) {
        document.getElementById('canvas-loading').style.display = isLoading ? 'flex' : 'none';
    }

    loadPages(pages) {
        this.pages = pages;
        if (pages.length > 0) {
            this.showPage(pages[0].page_number);
        }
    }

    async showPage(pageNumber) {
        this.setLoading(true);
        const pageData = this.pages.find(p => p.page_number === pageNumber);
        if (!pageData) return;

        this.currentPage = pageData;
        
        if (pageData.image_path) {
            try {
                // Ensure the image_path uses the API route for serving files if it's a server path
                // If it's a mock or full URL, it handles it.
                let imgUrl = pageData.image_path;
                if (!imgUrl.startsWith('http') && !imgUrl.startsWith('blob')) {
                    imgUrl = `/api/v1/files/${encodeURIComponent(imgUrl)}`;
                }
                
                const img = new Image();
                img.onload = () => {
                    this.currentImage = img;
                    this.setLoading(false);
                    this.draw();
                };
                img.onerror = () => {
                    this.currentImage = null;
                    this.setLoading(false);
                    this.drawPlaceholder(pageNumber);
                };
                img.src = imgUrl;
            } catch (e) {
                console.error('Error loading image', e);
                this.currentImage = null;
                this.setLoading(false);
                this.drawPlaceholder(pageNumber);
            }
        } else {
            this.currentImage = null;
            this.setLoading(false);
            this.drawPlaceholder(pageNumber);
        }
    }

    draw() {
        if (!this.currentImage && !this.currentPage) return;
        if (!this.currentImage) {
            this.drawPlaceholder(this.currentPage.page_number);
            return;
        }

        const img = this.currentImage;
        const containerWidth = this.container.clientWidth - 40;
        const containerHeight = this.container.clientHeight - 40;
        
        // Calculate scale to fit container while maintaining aspect ratio
        const scaleX = containerWidth / img.width;
        const scaleY = containerHeight / img.height;
        const baseScale = Math.min(scaleX, scaleY);
        
        const finalScale = baseScale * this.scale;
        
        this.canvas.width = img.width * finalScale;
        this.canvas.height = img.height * finalScale;
        
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        this.ctx.drawImage(img, 0, 0, this.canvas.width, this.canvas.height);

        if (this.showBoxes && this.currentPage.detected_elements) {
            this.renderBoundingBoxes(this.currentPage.detected_elements, finalScale);
        }
    }

    renderBoundingBoxes(elements, scale) {
        elements.forEach(el => {
            if (!el.bbox) return;
            // Assuming bbox is [x, y, width, height] in original image coordinates
            const [x, y, w, h] = el.bbox.map(val => val * scale);
            
            let strokeColor, fillColor;
            switch(el.type) {
                case 'SIGNATURE_BLOCK':
                    strokeColor = '#3b82f6'; fillColor = 'rgba(59, 130, 246, 0.2)'; break;
                case 'HANDWRITTEN_REDLINE':
                    strokeColor = '#f97316'; fillColor = 'rgba(249, 115, 22, 0.2)'; break;
                case 'STAMP_SEAL':
                    strokeColor = '#a855f7'; fillColor = 'rgba(168, 85, 247, 0.2)'; break;
                case 'INITIAL_MARK':
                    strokeColor = '#22c55e'; fillColor = 'rgba(34, 197, 94, 0.2)'; break;
                default:
                    strokeColor = '#ef4444'; fillColor = 'rgba(239, 68, 68, 0.2)';
            }

            this.ctx.strokeStyle = strokeColor;
            this.ctx.lineWidth = 2;
            this.ctx.fillStyle = fillColor;
            
            this.ctx.beginPath();
            this.ctx.rect(x, y, w, h);
            this.ctx.fill();
            this.ctx.stroke();

            // Label
            this.ctx.fillStyle = strokeColor;
            this.ctx.font = '12px Inter';
            const labelText = el.type.replace('_', ' ');
            const textWidth = this.ctx.measureText(labelText).width;
            
            this.ctx.fillRect(x, y - 20, textWidth + 10, 20);
            this.ctx.fillStyle = '#ffffff';
            this.ctx.fillText(labelText, x + 5, y - 5);
        });
    }

    drawPlaceholder(pageNumber) {
        const w = 600 * this.scale;
        const h = 800 * this.scale;
        
        this.canvas.width = w;
        this.canvas.height = h;
        
        this.ctx.fillStyle = '#ffffff';
        this.ctx.fillRect(0, 0, w, h);
        
        // Draw lines
        this.ctx.strokeStyle = '#e2e8f0';
        this.ctx.lineWidth = 12 * this.scale;
        this.ctx.lineCap = 'round';
        
        for (let i = 0; i < 10; i++) {
            const y = 100 + (i * 40);
            const lineWidth = i % 3 === 0 ? w * 0.5 : w * 0.8;
            this.ctx.beginPath();
            this.ctx.moveTo(50 * this.scale, y * this.scale);
            this.ctx.lineTo(50 * this.scale + lineWidth, y * this.scale);
            this.ctx.stroke();
        }

        // Overlay text
        this.ctx.fillStyle = '#94a3b8';
        this.ctx.font = `${24 * this.scale}px Inter`;
        this.ctx.textAlign = 'center';
        this.ctx.fillText(`Page ${pageNumber} (Text Mode)`, w/2, h/2);
    }

    zoomIn() {
        this.scale = Math.min(this.scale + 0.2, 3.0);
        this.draw();
        return this.scale;
    }

    zoomOut() {
        this.scale = Math.max(this.scale - 0.2, 0.5);
        this.draw();
        return this.scale;
    }

    toggleBoxes() {
        this.showBoxes = !this.showBoxes;
        this.draw();
    }
}
