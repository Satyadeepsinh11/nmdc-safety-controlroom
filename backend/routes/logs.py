import csv
import io
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.models import AuditLog

router = APIRouter(prefix="/api/logs", tags=["Audit Logs"])


class LogSchema(BaseModel):
    id: int
    timestamp: datetime
    user_id: str
    action: str
    module: str
    payload: str

    class Config:
        from_attributes = True


@router.get("", response_model=List[LogSchema])
def get_logs(db: Session = Depends(get_db)):
    logs = (
        db.query(AuditLog)
        .order_by(AuditLog.timestamp.desc())
        .limit(100)
        .all()
    )
    return logs


@router.get("/export")
def export_logs_csv(db: Session = Depends(get_db)):
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        ["ID", "Timestamp (UTC)", "User/Operator", "Module", "Action", "Payload / Meta"]
    )

    for log in logs:
        writer.writerow(
            [
                log.id,
                log.timestamp.isoformat(),
                log.user_id,
                log.module,
                log.action,
                log.payload,
            ]
        )

    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=nmdc_audit_export.csv"
        },
    )