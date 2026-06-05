"""加工记录 API (B16)"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.job_record import JobRecord
from app.schemas.job_record import JobRecordCreate, JobRecordOut

router = APIRouter()

@router.post("/save", response_model=JobRecordOut)
def save_job_record(record: JobRecordCreate, db: Session = Depends(get_db)):
    """保存加工记录（首检通过后调用）"""
    db_record = JobRecord(**record.model_dump())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

@router.get("/history", response_model=list[JobRecordOut])
def get_history(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """查询历史记录"""
    return db.query(JobRecord).offset(skip).limit(limit).all()
