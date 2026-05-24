"""
ETL Pipeline Orchestrator
Runs Extract -> Transform -> Load and logs each run to etl_run_logs.
"""

import time
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from database import SessionLocal
import models
from etl.extract import extract_all
from etl.transform import transform_all
from etl.load import load_all


def run_pipeline() -> dict:
    """Execute the full ETL pipeline and return a summary dict."""
    session = SessionLocal()
    log = models.ETLRunLog(run_at=datetime.utcnow(), status="running")
    session.add(log)
    session.commit()

    start = time.time()
    try:
        print("=" * 60)
        print(f"[ETL] Pipeline started at {log.run_at}")

        # ── Extract ──────────────────────────────────────────────
        print("[ETL] Step 1: Extract")
        raw = extract_all()
        records_extracted = raw["total_records"]
        print(f"[ETL] Extracted {records_extracted} raw records")

        # ── Transform ────────────────────────────────────────────
        print("[ETL] Step 2: Transform")
        clean = transform_all(raw)
        records_transformed = clean["total_records"]
        print(f"[ETL] Transformed -> {records_transformed} clean records")

        # ── Load ─────────────────────────────────────────────────
        print("[ETL] Step 3: Load")
        records_loaded = load_all(session, clean)
        print(f"[ETL] Loaded {records_loaded} records into DB")

        duration = round(time.time() - start, 2)

        log.records_extracted = records_extracted
        log.records_transformed = records_transformed
        log.records_loaded = records_loaded
        log.status = "success"
        log.duration_seconds = duration
        session.commit()

        summary = {
            "status": "success",
            "run_id": log.id,
            "run_at": log.run_at.isoformat(),
            "records_extracted": records_extracted,
            "records_transformed": records_transformed,
            "records_loaded": records_loaded,
            "duration_seconds": duration,
        }
        print(f"[ETL] Pipeline completed in {duration}s")
        print("=" * 60)
        return summary

    except Exception as exc:
        duration = round(time.time() - start, 2)
        log.status = "failed"
        log.error_message = str(exc)
        log.duration_seconds = duration
        session.commit()
        print(f"[ETL] Pipeline FAILED: {exc}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    result = run_pipeline()
    print(result)
