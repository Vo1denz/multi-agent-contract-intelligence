"""Contract endpoints."""
from __future__ import annotations
import os
import uuid
import asyncio
from typing import Dict, Any
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from pydantic import BaseModel

from src.api.schemas.contract_schema import ContractUploadResponse, AnalysisReportResponse

try:
    from config.settings import settings
except ImportError:
    class MockSettings:
        upload_dir = "uploads"
        max_upload_size_mb = 10
        clauseiq_mode = "lite"
        app_host = "0.0.0.0"
        app_port = 8000
        base_dir = "."
    settings = MockSettings()

try:
    from src.orchestration.runner import ClauseIQRunner
except ImportError:
    class ClauseIQRunner:
        def run(self, contract_id, file_path):
            return {"contract_id": contract_id, "file_path": file_path, "execution_complete": True}

router = APIRouter(prefix="/api/v1/contracts", tags=["Contracts"])

_analysis_cache: Dict[str, Any] = {}
_upload_cache: Dict[str, Any] = {}

@router.post("/upload", response_model=ContractUploadResponse)
async def upload_contract(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
        
    ext = file.filename.split(".")[-1].lower()
    if ext not in ["pdf", "png", "jpg", "jpeg"]:
        raise HTTPException(status_code=400, detail="Unsupported file type")
        
    contract_id = uuid.uuid4().hex[:12]
    os.makedirs(settings.upload_dir, exist_ok=True)
    file_path = os.path.join(settings.upload_dir, f"{contract_id}_{file.filename}")
    
    try:
        contents = await file.read()
        if len(contents) > settings.max_upload_size_mb * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File too large")
        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    _upload_cache[contract_id] = {"file_path": file_path, "filename": file.filename}
        
    return ContractUploadResponse(
        contract_id=contract_id,
        filename=file.filename,
        file_path=file_path,
        status="uploaded"
    )

@router.post("/{contract_id}/analyze", response_model=AnalysisReportResponse)
async def analyze_contract(contract_id: str):
    # Resolve file path from upload cache
    upload_info = _upload_cache.get(contract_id, {})
    file_path = upload_info.get("file_path", "")

    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Uploaded file not found for this contract_id")
        
    runner = ClauseIQRunner()
    
    try:
        result = await asyncio.to_thread(runner.run, contract_id, file_path)
        _analysis_cache[contract_id] = result
        return AnalysisReportResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/{contract_id}/report", response_model=AnalysisReportResponse)
async def get_report(contract_id: str):
    if contract_id not in _analysis_cache:
        raise HTTPException(status_code=404, detail="Report not found")
    return AnalysisReportResponse(**_analysis_cache[contract_id])
