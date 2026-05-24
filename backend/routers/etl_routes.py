"""
ETL API Routes – Phase 2
Endpoints to trigger and inspect ETL pipeline runs.
"""

from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from fastapi import Depends

import models
from database import get_db

router = APIRouter(prefix="/etl", tags=["ETL"])


@router.post("/run", summary="Trigger the full ETL pipeline")
def trigger_etl():
    """
    Runs Extract -> Transform -> Load pipeline against the datasets/ CSV files.
    Rebuilds all analytics tables on completion.
    """
    try:
        from etl.pipeline import run_pipeline
        result = run_pipeline()
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"ETL pipeline failed: {str(exc)}")


@router.get("/logs", summary="List all ETL run history")
def get_etl_logs(db: Session = Depends(get_db)):
    logs = (
        db.query(models.ETLRunLog)
        .order_by(models.ETLRunLog.run_at.desc())
        .limit(50)
        .all()
    )
    return [
        {
            "id": l.id,
            "run_at": l.run_at.isoformat() if l.run_at else None,
            "status": l.status,
            "records_extracted": l.records_extracted,
            "records_transformed": l.records_transformed,
            "records_loaded": l.records_loaded,
            "duration_seconds": l.duration_seconds,
            "error_message": l.error_message,
        }
        for l in logs
    ]


@router.get("/status", summary="Latest ETL run status")
def get_etl_status(db: Session = Depends(get_db)):
    latest = (
        db.query(models.ETLRunLog)
        .order_by(models.ETLRunLog.run_at.desc())
        .first()
    )
    if not latest:
        return {"status": "never_run", "message": "No ETL runs recorded yet. POST /etl/run to start."}
    return {
        "id": latest.id,
        "run_at": latest.run_at.isoformat() if latest.run_at else None,
        "status": latest.status,
        "records_extracted": latest.records_extracted,
        "records_transformed": latest.records_transformed,
        "records_loaded": latest.records_loaded,
        "duration_seconds": latest.duration_seconds,
        "error_message": latest.error_message,
    }
