from dataclasses import dataclass
from datetime import datetime

from fastapi import Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.security import hash_token
from app.database.connection import get_db
from app.models.project import GuestSession, Project, ProjectMembership
from app.models.user import User


@dataclass(frozen=True)
class ProjectAccess:
    project_id: int
    permission: str
    user_id: int | None = None
    guest_session_id: int | None = None

    @property
    def can_edit(self) -> bool:
        return self.permission in {"owner", "editor"}


def require_project_access(
    request: Request,
    x_project_id: int | None = Header(default=None, alias="X-Project-ID"),
    db: Session = Depends(get_db),
) -> ProjectAccess:
    if x_project_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Selecciona un proyecto")
    project = db.get(Project, x_project_id)
    if not project or project.archived_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proyecto no encontrado")

    token = request.cookies.get("oh_session")
    if token:
        from app.models.user import UserSession
        session = db.query(UserSession).filter(UserSession.token_hash == hash_token(token)).first()
        if session and not session.revoked_at and session.expires_at > datetime.utcnow() and session.user.active:
            user: User = session.user
            if user.must_change_password:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Debes cambiar tu contraseña antes de continuar")
            if user.system_role == "superadmin":
                access = ProjectAccess(project_id=project.id_project, permission="owner", user_id=user.id_user)
            else:
                membership = db.query(ProjectMembership).filter_by(project_id=project.id_project, user_id=user.id_user).first()
                if not membership:
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No perteneces a este proyecto")
                access = ProjectAccess(project_id=project.id_project, permission=membership.permission, user_id=user.id_user)
            if request.method not in {"GET", "HEAD", "OPTIONS"} and not access.can_edit:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tu acceso es de solo lectura")
            request.state.project_access = access
            return access

    guest_token = request.cookies.get("oh_guest_session")
    guest = db.query(GuestSession).filter(GuestSession.token_hash == hash_token(guest_token)).first() if guest_token else None
    if not guest or guest.expires_at <= datetime.utcnow() or guest.invite.project_id != project.id_project:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Debes iniciar sesión o usar una invitación válida")
    access = ProjectAccess(project_id=project.id_project, permission=guest.invite.permission, guest_session_id=guest.id_guest_session)
    if request.method not in {"GET", "HEAD", "OPTIONS"} and not access.can_edit:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tu invitación es de solo lectura")
    request.state.project_access = access
    return access

