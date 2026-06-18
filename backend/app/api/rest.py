from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel, Field
from redis import Redis
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import ModelRecord, Sample, TrainingJob, get_db
from app.core.features import validate_feature

router = APIRouter()


class SampleIn(BaseModel):
    label: str = Field(min_length=1, max_length=64)
    mode: str = Field(pattern="^(static|dynamic)$")
    feature: list[float] | list[list[float]]


class TrainIn(BaseModel):
    mode: str = Field(pattern="^(static|dynamic)$")


def redis_client() -> Redis:
    return Redis.from_url(settings.redis_url, decode_responses=True)


@router.get("/labels")
def labels() -> dict:
    return {"static": settings.static_labels, "dynamic": settings.dynamic_labels}


@router.post("/samples")
def create_sample(payload: SampleIn, db: Session = Depends(get_db)) -> dict:
    if payload.mode == "static":
        try:
            validate_feature(payload.feature)  # type: ignore[arg-type]
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
    elif len(payload.feature) != settings.seq_len:
        raise HTTPException(status_code=422, detail=f"dynamic sample must contain {settings.seq_len} frames")

    sample = Sample(label=payload.label, mode=payload.mode, feature=payload.feature)
    db.add(sample)
    db.commit()
    db.refresh(sample)
    return {"id": sample.id, "label": sample.label, "mode": sample.mode}


@router.get("/samples/counts")
def sample_counts(db: Session = Depends(get_db)) -> dict:
    rows = db.execute(
        select(Sample.mode, Sample.label, func.count(Sample.id)).group_by(Sample.mode, Sample.label)
    ).all()
    counts: dict[str, dict[str, int]] = {"static": {}, "dynamic": {}}
    for mode, label, count in rows:
        counts[mode][label] = count
    return counts


@router.get("/models")
def models(db: Session = Depends(get_db)) -> list[dict]:
    rows = db.execute(select(ModelRecord).order_by(ModelRecord.created_at.desc())).scalars().all()
    return [
        {
            "id": row.id,
            "name": row.name,
            "mode": row.mode,
            "path": row.path,
            "accuracy": row.accuracy,
            "active": row.active,
            "createdAt": row.created_at.isoformat(),
        }
        for row in rows
    ]


@router.post("/train")
def train(payload: TrainIn, background_tasks: BackgroundTasks, db: Session = Depends(get_db)) -> dict:
    job = TrainingJob(mode=payload.mode, status="queued")
    db.add(job)
    db.commit()
    db.refresh(job)
    background_tasks.add_task(mark_training_complete, job.id, payload.mode)
    return {"jobId": job.id, "status": job.status}


@router.get("/train/{job_id}")
def train_status(job_id: int, db: Session = Depends(get_db)) -> dict:
    job = db.get(TrainingJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="training job not found")
    return {
        "id": job.id,
        "mode": job.mode,
        "status": job.status,
        "message": job.message,
        "modelId": job.model_id,
        "createdAt": job.created_at.isoformat(),
        "finishedAt": job.finished_at.isoformat() if job.finished_at else None,
    }


@router.get("/metrics")
def metrics(db: Session = Depends(get_db)) -> dict:
    sample_total = db.scalar(select(func.count(Sample.id))) or 0
    model_total = db.scalar(select(func.count(ModelRecord.id))) or 0
    try:
        redis_ok = bool(redis_client().ping())
    except Exception:
        redis_ok = False
    return {"samples": sample_total, "models": model_total, "redis": redis_ok}


def mark_training_complete(job_id: int, mode: str) -> None:
    db = next(get_db())
    try:
        job = db.get(TrainingJob, job_id)
        if not job:
            return
        job.status = "finished"
        job.message = "训练接口已打通；采集足量样本后运行 scripts/train_static.py 或 train_dynamic.py 生成模型。"
        job.finished_at = datetime.utcnow()
        db.commit()
        redis_client().set(f"train:{job_id}:status", job.status, ex=3600)
    finally:
        db.close()
