import sys
import os
import math
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import uuid
import shutil
import json
from pathlib import Path
from typing import Any
from fastapi import FastAPI, BackgroundTasks, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse


def _sanitize_for_json(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _sanitize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_sanitize_for_json(v) for v in obj]
    if isinstance(obj, float):
        if math.isinf(obj) or math.isnan(obj):
            return str(obj)
    return obj


class SafeJSONResponse(JSONResponse):
    def render(self, content: Any) -> bytes:
        return json.dumps(
            _sanitize_for_json(content),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")


app = FastAPI(
    title="Automated Financial Controls & Continuous Auditing Engine (AFC-CAE)",
    version="1.1",
    description="REST API Mesin Kontrol Detektif Keuangan Otomatis & Audit Berkelanjutan."
)

UPLOAD_DIR = Path("tmp/afc_cae_uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

CONFIG_PATH = "config/audit_config_v1.yaml"

REPORTS_DB = {}

def async_pipeline_worker(run_id: str, temp_file_path: Path):
    try:
        from src.pipeline import run_full_audit_pipeline
        report_manifest = run_full_audit_pipeline(str(temp_file_path), CONFIG_PATH)
        REPORTS_DB[run_id] = {
            "status": "SELESAI",
            "results": report_manifest
        }
    except Exception as e:
        REPORTS_DB[run_id] = {
            "status": "ERROR",
            "reason": str(e)
        }
    finally:
        if temp_file_path.exists():
            os.remove(temp_file_path)

@app.get("/health")
def health_check():
    return {"status": "UP", "engine_version": "1.1", "environment": "Windows-Local"}

@app.post("/api/v1/audit/ingest")
async def ingest_dataset(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    if not file.filename.endswith(('.csv', '.parquet')):
        raise HTTPException(
            status_code=415,
            detail="Format file tidak didukung. AFC-CAE v1.1 hanya menerima ekstensi .csv dan .parquet."
        )

    run_id = f"AFC-CAE-RUN-{uuid.uuid4().hex[:12].upper()}"
    file_extension = Path(file.filename).suffix
    temp_file_path = UPLOAD_DIR / f"{run_id}{file_extension}"

    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    REPORTS_DB[run_id] = {"status": "DITERIMA", "filename": file.filename}
    background_tasks.add_task(async_pipeline_worker, run_id, temp_file_path)

    return JSONResponse(
        status_code=202,
        content={
            "run_id": run_id,
            "status": "DITERIMA",
            "message": "Pipeline kontrol audit telah dimulai di latar belakang.",
            "status_endpoint": f"/api/v1/audit/status/{run_id}"
        }
    )

@app.get("/api/v1/audit/status/{run_id}", response_class=SafeJSONResponse)
def get_audit_status(run_id: str):
    if run_id not in REPORTS_DB:
        raise HTTPException(status_code=404, detail="Run ID audit tidak ditemukan di dalam sistem.")
    return REPORTS_DB[run_id]
