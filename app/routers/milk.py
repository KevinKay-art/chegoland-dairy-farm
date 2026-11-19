"""Milk production API routers."""

from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.milk_record import MilkRecord
from app.models.cow import Cow
from app.models.user import User
from app.utils.security import require_role
from datetime import date

router = APIRouter()


@router.get("/api/v1/milk")
async def api_list_milk_records(db: Session = Depends(get_db),
                                current_user: User = Depends(require_role(["admin"]))):
    records = db.query(MilkRecord).order_by(MilkRecord.date.desc()).all()
    return [
        {
            "id": r.id, "cow_id": r.cow_id, "date": r.date.isoformat() if hasattr(r.date, "isoformat") else str(r.date),
            "session": r.session, "yield_litres": r.yield_litres,
            "used_by_calves": r.used_by_calves, "spoiled": r.spoiled,
            "available_for_sale": r.available_for_sale, "notes": r.notes,
        }
        for r in records
    ]


@router.post("/api/v1/milk")
async def api_record_milk(cow_id: str = Form(...), date: str = Form(...),
                          session: str = Form(...), yield_litres: float = Form(...),
                          used_by_calves: float = Form(0.0), spoiled: float = Form(0.0),
                          notes: str = Form(""),
                          db: Session = Depends(get_db),
                          current_user: User = Depends(require_role(["admin"]))):
    import uuid
    from datetime import date as date_class
    cow = db.query(Cow).filter(Cow.id == cow_id).first()
    if not cow:
        raise HTTPException(status_code=404, detail="Cow not found")

    record_date = date_class.fromisoformat(date)
    available = yield_litres - used_by_calves - spoiled

    record = MilkRecord(
        id=str(uuid.uuid4()), cow_id=cow_id, date=record_date, session=session,
        yield_litres=yield_litres, used_by_calves=used_by_calves, spoiled=spoiled,
        available_for_sale=available, notes=notes or None,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return {"id": record.id, "message": "Milk record created", "available_for_sale": available}


@router.delete("/api/v1/milk/{record_id}")
async def api_delete_milk_record(record_id: str, db: Session = Depends(get_db),
                                 current_user: User = Depends(require_role(["admin"]))):
    record = db.query(MilkRecord).filter(MilkRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    db.delete(record)
    db.commit()
    return {"message": "Record deleted"}