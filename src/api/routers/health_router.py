"""Health check endpoints."""
from __future__ import annotations
from fastapi import APIRouter
from typing import Dict, Any

try:
    from config.settings import settings
except ImportError:
    class MockSettings:
        clauseiq_mode = "lite"
    settings = MockSettings()

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("")
async def get_health() -> Dict[str, Any]:
    return {
        "status": "ok",
        "mode": getattr(settings, "clauseiq_mode", "unknown"),
        "version": "1.0.0"
    }

@router.get("/models")
async def get_models() -> Dict[str, Any]:
    mode = getattr(settings, "clauseiq_mode", "lite")
    if mode == "full":
        return {
            "models": {
                "layout": "LayoutLMv3",
                "vision": "Donut",
                "language": "LLaMA/Mistral"
            }
        }
    return {
        "models": {
            "layout": "heuristics",
            "vision": "disabled",
            "language": "mock"
        }
    }
