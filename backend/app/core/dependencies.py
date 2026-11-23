from datetime import datetime

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.security import SESSION_COOKIE, hash_token
from app.database.connection import get_db
from app.models.user import User, UserSession


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Debes iniciar sesión")

    session = db.query(UserSession).filter(UserSession.token_hash == hash_token(token)).first()
    if not session or session.revoked_at or session.expires_at <= datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="La sesión no es válida o expiró")
    if not session.user.active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="El usuario está desactivado")
    return session.user


def require_superadmin(user: User = Depends(get_current_user)) -> User:
    if user.system_role != "superadmin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Se requiere superadmin")
    return user

