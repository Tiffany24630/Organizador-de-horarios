from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.core.dependencies import require_superadmin
from app.core.security import hash_password, normalize_email, validate_password
from app.database.connection import get_db
from app.models.user import PasswordRecoveryRequest, User

router = APIRouter(prefix="/admin", tags=["Administration"])


class CreateUserRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    temporary_password: str = Field(min_length=12, max_length=200)


class ResetUserPasswordRequest(BaseModel):
    temporary_password: str = Field(min_length=12, max_length=200)


@router.post("/users")
def create_user(data: CreateUserRequest, _: User = Depends(require_superadmin), db: Session = Depends(get_db)):
    email = normalize_email(str(data.email))
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=409, detail="El correo ya está registrado")
    try:
        validate_password(data.temporary_password)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    user = User(name=data.name.strip(), email=email, password_hash=hash_password(data.temporary_password), must_change_password=True)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id_user": user.id_user, "name": user.name, "email": user.email, "must_change_password": True}


@router.get("/users")
def list_users(_: User = Depends(require_superadmin), db: Session = Depends(get_db)):
    return [{"id_user": u.id_user, "name": u.name, "email": u.email, "active": u.active, "system_role": u.system_role} for u in db.query(User).order_by(User.name).all()]


@router.post("/users/{user_id}/reset-password")
def reset_user_password(user_id: int, data: ResetUserPasswordRequest, _: User = Depends(require_superadmin), db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    try:
        validate_password(data.temporary_password)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    user.password_hash = hash_password(data.temporary_password)
    user.must_change_password = True
    for session in user.sessions:
        session.revoked_at = datetime.utcnow()
    db.commit()
    return {"detail": "Contraseña temporal establecida"}


@router.get("/recovery-requests")
def list_recovery_requests(_: User = Depends(require_superadmin), db: Session = Depends(get_db)):
    return db.query(PasswordRecoveryRequest).order_by(PasswordRecoveryRequest.created_at.desc()).all()

