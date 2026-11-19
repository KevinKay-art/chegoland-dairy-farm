"""Health records API router (admin only)."""
from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.health_record import HealthRecord
from app.models.cow import Cow
from app.models.user import User
from app.utils.security import require_role
from app.config import settings
import uuid
from datetime import date

router = APIRouter(prefix="/api/v1/health-records")


@router.get("", response_model=list)
async def api_list_health_records(db: Session = Depends(get_db),
                                  current_user: User = Depends(require_role(["admin"]))):
    records = db.query(HealthRecord).order_by(HealthRecord.date.desc()).all()
    return [
        {
            "id": r.id, "cow_id": r.cow_id, "record_type": r.record_type,
            "title": r.title, "description": r.description, "date": r.date.isoformat() if hasattr(r.date, "isoformat") else str(r.date),
            "next_due_date": r.next_due_date.isoformat() if r.next_due_date and hasattr(r.next_due_date, "isoformat") else (str(r.next_due_date) if r.next_due_date else None),
            "cost": r.cost, "vet_name": r.vet_name, "notes": r.notes,
        }
        for r in records
    ]


@router.post("", status_code=status.HTTP_201_CREATED)
async def api_create_health_record(cow_id: str = Form(...), record_type: str = Form(...),
                                   title: str = Form(...), description: str = Form(""),
                                   date: str = Form(...), next_due_date: str = Form(""),
                                   cost: str = Form(None), vet_name: str = Form(None),
                                   notes: str = Form(""),
                                   db: Session = Depends(get_db),
                                   current_user: User = Depends(require_role(["admin"]))):
    cow = db.query(Cow).filter(Cow.id == cow_id).first()
    if not cow:
        raise HTTPException(status_code=404, detail="Cow not found")
    record = HealthRecord(
        id=str(uuid.uuid4()), cow_id=cow_id, record_type=record_type, title=title,
        description=description or None, date=date.fromisoformat(date),
        next_due_date=date.fromisoformat(next_due_date) if next_due_date else None,
        cost=cost, vet_name=vet_name, notes=notes or None,
    )
    db.add(record)
    db.commit()
    return {"id": record.id, "message": "Health record created"}


@router.delete("/{record_id}")
async def api_delete_health_record(record_id: str, db: Session = Depends(get_db),
                                   current_user: User = Depends(require_role(["admin"]))):
    record = db.query(HealthRecord).filter(HealthRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    db.delete(record)
    db.commit()
    return {"message": "Health record deleted"}
