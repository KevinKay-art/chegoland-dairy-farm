"""Cows API routers."""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.cow import Cow
from app.models.user import User
from app.utils.security import require_role
from app.utils.image import save_uploaded_image
from app.config import settings
from pathlib import Path
import uuid

router = APIRouter()
UPLOAD_DIR = Path("app/static/uploads/cows")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.get("/api/v1/cows")
async def api_list_cows(db: Session = Depends(get_db)):
    cows = db.query(Cow).all()
    return [
        {
            "id": c.id, "tag_number": c.tag_number, "name": c.name, "breed": c.breed,
            "date_of_birth": c.date_of_birth.isoformat() if c.date_of_birth else None,
            "photo_url": c.photo_url, "status": c.status,
            "daily_avg_yield": c.daily_avg_yield, "notes": c.notes,
        }
        for c in cows
    ]


@router.post("/api/v1/cows")
async def api_create_cow(tag_number: str = Form(...), name: str = Form(...), breed: str = Form(...),
                         date_of_birth: str = Form(None), photo: UploadFile = File(None),
                         status: str = Form("lactating"), daily_avg_yield: float = Form(0.0),
                         notes: str = Form(""),
                         db: Session = Depends(get_db),
                         current_user: User = Depends(require_role(["admin"]))):
    photo_url = None
    if photo:
        photo_url = save_uploaded_image(photo, UPLOAD_DIR, url_prefix="/static/uploads/cows")

    cow = Cow(
        id=str(uuid.uuid4()), tag_number=tag_number, name=name, breed=breed,
        photo_url=photo_url, status=status, daily_avg_yield=daily_avg_yield, notes=notes or None,
    )
    from datetime import date
    if date_of_birth:
        cow.date_of_birth = date.fromisoformat(date_of_birth)
    db.add(cow)
    db.commit()
    db.refresh(cow)
    return {"id": cow.id, "message": "Cow created"}


@router.put("/api/v1/cows/{cow_id}")
async def api_update_cow(cow_id: str, name: str = Form(None), breed: str = Form(None),
                         status: str = Form(None), daily_avg_yield: float = Form(None),
                         notes: str = Form(None),
                         db: Session = Depends(get_db),
                         current_user: User = Depends(require_role(["admin"]))):
    cow = db.query(Cow).filter(Cow.id == cow_id).first()
    if not cow:
        raise HTTPException(status_code=404, detail="Cow not found")
    if name is not None: cow.name = name
    if breed is not None: cow.breed = breed
    if status is not None: cow.status = status
    if daily_avg_yield is not None: cow.daily_avg_yield = daily_avg_yield
    if notes is not None: cow.notes = notes
    db.commit()
    return {"id": cow.id, "message": "Cow updated"}


@router.delete("/api/v1/cows/{cow_id}")
async def api_delete_cow(cow_id: str, db: Session = Depends(get_db),
                         current_user: User = Depends(require_role(["admin"]))):
    cow = db.query(Cow).filter(Cow.id == cow_id).first()
    if not cow:
        raise HTTPException(status_code=404, detail="Cow not found")
    db.delete(cow)
    db.commit()
    return {"message": "Cow deleted"}