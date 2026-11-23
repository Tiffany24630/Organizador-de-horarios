from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.security import (
    SESSION_COOKIE,
    hash_password,
    hash_token,
    new_session_token,
    normalize_email,
    session_expiry,
    cookie_settings,
    validate_password,
    verify_password,
)
from app.database.connection import get_db
from app.models.user import PasswordRecoveryRequest, User, UserSession
from app.models.project import GuestSession, ProjectMembership

router = APIRouter(prefix="/auth", tags=["Authentication"])


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class RecoveryRequest(BaseModel):
    email: EmailStr
    message: str = Field(min_length=5, max_length=500)


def _set_session_cookie(response: Response, token: str) -> None:
    secure, samesite = cookie_settings()
    response.set_cookie(
        SESSION_COOKIE,
        token,
        max_age=14 * 24 * 60 * 60,
        httponly=True,
        secure=secure,
        samesite=samesite,
        path="/",
    )


def _user_payload(user: User) -> dict:
    return {
        "id_user": user.id_user,
        "name": user.name,
        "email": user.email,
        "system_role": user.system_role,
        "must_change_password": user.must_change_password,
    }


@router.post("/login")
def login(data: LoginRequest, request: Request, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == normalize_email(str(data.email))).first()
    if not user or not user.active or not verify_password(user.password_hash, data.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Correo o contraseña incorrectos")

    token, token_hash = new_session_token()
    db.add(UserSession(user_id=user.id_user, token_hash=token_hash, expires_at=session_expiry()))
    guest_token = request.cookies.get("oh_guest_session")
    if guest_token:
        guest = db.query(GuestSession).filter(GuestSession.token_hash == hash_token(guest_token), GuestSession.user_id.is_(None)).first()
        if guest and guest.expires_at > datetime.utcnow():
            membership = db.query(ProjectMembership).filter_by(project_id=guest.invite.project_id, user_id=user.id_user).first()
            if membership is None:
                db.add(ProjectMembership(project_id=guest.invite.project_id, user_id=user.id_user, permission=guest.invite.permission))
            elif membership.permission == "viewer" and guest.invite.permission == "editor":
                membership.permission = "editor"
            guest.user_id = user.id_user
    db.commit()
    _set_session_cookie(response, token)
    return _user_payload(user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    token = request.cookies.get(SESSION_COOKIE)
    if token:
        session = db.query(UserSession).filter(UserSession.token_hash == hash_token(token)).first()
        if session:
            session.revoked_at = datetime.utcnow()
            db.commit()
    response.delete_cookie(SESSION_COOKIE, path="/")


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return _user_payload(user)


@router.post("/change-password")
def change_password(data: ChangePasswordRequest, request: Request, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not verify_password(user.password_hash, data.current_password):
        raise HTTPException(status_code=400, detail="La contraseña actual no es correcta")
    try:
        validate_password(data.new_password)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    user.password_hash = hash_password(data.new_password)
    user.must_change_password = False
    current_hash = hash_token(request.cookies.get(SESSION_COOKIE, ""))
    for session in user.sessions:
        if session.token_hash != current_hash:
            session.revoked_at = datetime.utcnow()
    db.commit()
    return {"detail": "Contraseña actualizada. Inicia sesión nuevamente."}


@router.post("/recovery-requests", status_code=status.HTTP_202_ACCEPTED)
def create_recovery_request(data: RecoveryRequest, db: Session = Depends(get_db)):
    request = PasswordRecoveryRequest(email=normalize_email(str(data.email)), message=data.message.strip())
    db.add(request)
    db.commit()
    # Do not reveal whether the email belongs to a user.
    return {"detail": "La solicitud fue enviada al superadmin."}

