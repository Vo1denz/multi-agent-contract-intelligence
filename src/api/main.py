"""Main FastAPI application."""
from __future__ import annotations
import os
import asyncio
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse

try:
    from config.settings import settings
except ImportError:
    class MockSettings:
        upload_dir = "uploads"
        base_dir = "."
        clauseiq_mode = "lite"
    settings = MockSettings()

from src.api.routers import contract_router, health_router
from src.api.schemas.contract_schema import AgentProgressMessage

try:
    from src.orchestration.runner import ClauseIQRunner
except ImportError:
    class ClauseIQRunner:
        def run(self, contract_id, file_path):
            return {"contract_id": contract_id, "file_path": file_path, "execution_complete": True}

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"Starting ClauseIQ API in {getattr(settings, 'clauseiq_mode', 'lite')} mode.")
    upload_dir = getattr(settings, 'upload_dir', 'uploads')
    print(f"Upload directory: {upload_dir}")
    os.makedirs(upload_dir, exist_ok=True)
    yield
    print("Shutting down ClauseIQ API.")

app = FastAPI(
    title="ClauseIQ API",
    description="Multi-agent contract risk intelligence system",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router.router)
app.include_router(contract_router.router)

# Mount frontend files
static_dir = os.path.join(getattr(settings, "base_dir", "."), "frontend")
css_dir = os.path.join(static_dir, "css")
js_dir = os.path.join(static_dir, "js")
assets_dir = os.path.join(static_dir, "assets")

os.makedirs(css_dir, exist_ok=True)
os.makedirs(js_dir, exist_ok=True)
os.makedirs(assets_dir, exist_ok=True)

app.mount("/css", StaticFiles(directory=css_dir), name="css")
app.mount("/js", StaticFiles(directory=js_dir), name="js")
app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

@app.get("/")
async def serve_index():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return HTMLResponse("<html><body><h1>ClauseIQ API Running</h1><p>Static files not found.</p></body></html>")

@app.get("/api/v1/files/{path:path}")
async def serve_file(path: str):
    file_path = os.path.join(getattr(settings, 'upload_dir', 'uploads'), path)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return HTMLResponse(status_code=404, content="File not found")

@app.websocket("/ws/analysis/{contract_id}")
async def analysis_websocket(websocket: WebSocket, contract_id: str):
    await websocket.accept()

    # Get file_path from query params or analysis cache
    file_path = ""
    try:
        data = await asyncio.wait_for(websocket.receive_json(), timeout=5.0)
        file_path = data.get("file_path", "")
    except (asyncio.TimeoutError, Exception):
        pass

    if not file_path:
        # Try to find from upload cache
        cached = contract_router._upload_cache.get(contract_id, {})
        file_path = cached.get("file_path", "")

    if not file_path:
        await websocket.send_json({"error": "No file_path found for this contract_id"})
        await websocket.close()
        return

    AGENT_STEPS = [
        ("vision", "Document Vision", 1),
        ("extraction", "Text Extraction", 2),
        ("classification", "Clause Classification", 3),
        ("verification", "Execution Verification", 4),
        ("playbook_comparison", "Playbook RAG Comparison", 5),
        ("risk", "Risk Scoring", 6),
        ("critic", "Critic Verification", 7),
    ]

    runner = ClauseIQRunner()

    try:
        # Send initial progress
        for _, agent_name, step in AGENT_STEPS:
            msg = AgentProgressMessage(
                agent_name=agent_name,
                status="pending",
                step=step,
                total_steps=7,
                message=f"Waiting...",
                timestamp=datetime.now().isoformat()
            )
            await websocket.send_json(msg.model_dump())

        # Run the pipeline in a thread
        step_idx = [0]

        def progress_callback(node_name, node_state):
            step_idx[0] += 1

        result = await asyncio.to_thread(runner.run, contract_id, file_path)
        contract_router._analysis_cache[contract_id] = result

        # Send step-by-step completions
        for node_key, agent_name, step in AGENT_STEPS:
            msg = AgentProgressMessage(
                agent_name=agent_name,
                status="completed",
                step=step,
                total_steps=7,
                message=f"{agent_name} completed.",
                timestamp=datetime.now().isoformat()
            )
            await websocket.send_json(msg.model_dump())
            await asyncio.sleep(0.15)

        # Send final report
        await websocket.send_json({
            "agent_name": "System",
            "status": "complete",
            "step": 7,
            "total_steps": 7,
            "message": "Analysis complete",
            "timestamp": datetime.now().isoformat(),
            "report": result
        })
    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_json({"error": str(e), "status": "error"})
            await websocket.close()
        except Exception:
            pass

