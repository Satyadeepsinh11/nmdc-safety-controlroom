from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.models import Incident

router = APIRouter(prefix="/api/incidents", tags=["Incidents"])


class IncidentSchema(BaseModel):
    id: int
    incident_code: str
    timestamp: datetime
    node_id: str
    severity: str
    description: str
    status: str
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class IncidentAckSchema(BaseModel):
    status: str
    notes: Optional[str] = ""


@router.get("", response_model=List[IncidentSchema])
def get_incidents(db: Session = Depends(get_db)):
    return db.query(Incident).order_by(Incident.timestamp.desc()).all()


@router.put("/{incident_id}/acknowledge")
def acknowledge_incident(
    incident_id: int, payload: IncidentAckSchema, db: Session = Depends(get_db)
):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    incident.status = payload.status
    incident.notes = payload.notes
    db.commit()
    return {"message": f"Incident {incident_id} updated successfully"}