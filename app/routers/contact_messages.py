"""Contact messages API router: public create, admin list."""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.contact import ContactMessage
from app.models.user import User
from app.utils.security import require_role, get_current_user_optional
from app.config import settings
import uuid
from datetime import datetime, timezone

router = APIRouter(prefix="/api/v1/contact-messages")


@router.post("", status_code=status.HTTP_201_CREATED)
async def api_create_contact_message(request: Request, db: Session = Depends(get_db)):
    body = await request.json()
    msg = ContactMessage(
        id=str(uuid.uuid4()), name=body.get("name", ""), email=body.get("email", ""),
        phone=body.get("phone"), message=body.get("message", ""),
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    if not msg.name or not msg.email or not msg.message:
        raise HTTPException(status_code=400, detail="Name, email and message are required")
    db.add(msg)
    db.commit()
    return {"id": msg.id, "message": "Message sent"}


@router.get("", response_model=list)
async def api_list_contact_messages(db: Session = Depends(get_db),
                                    current_user: User = Depends(require_role(["admin"]))):
    messages = db.query(ContactMessage).order_by(ContactMessage.created_at.desc()).all()
    return [
        {"id": m.id, "name": m.name, "email": m.email, "phone": m.phone,
         "message": m.message, "created_at": m.created_at}
        for m in messages
    ]
