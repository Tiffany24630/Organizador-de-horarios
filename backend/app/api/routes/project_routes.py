from datetime import datetime, timedelta

from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, VerifyMismatchError
from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.security import cookie_settings, hash_token, new_invite_token, normalize_email
from app.database.connection import get_db
from app.models.project import GuestSession, Project, ProjectInvite, ProjectMembership
from app.models.user import User

router = APIRouter(prefix="/projects", tags=["Projects"])
guest_password_hasher = PasswordHasher()
GUEST_COOKIE = "oh_guest_session"


class ProjectCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    description: str | None = Field(default=None, max_length=1000)
    guest_access_enabled: bool = True
    guest_key_required: bool = False


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=150)
    description: str | None = Field(default=None, max_length=1000)
    guest_access_enabled: bool | None = None
    guest_key_required: bool | None = None


class InviteCreate(BaseModel):
    permission: str = Field(pattern="^(viewer|editor)$")
    label: str | None = Field(default=None, max_length=120)
    expires_in_hours: int | None = Field(default=None, ge=1, le=24 * 30)
    access_key: str | None = Field(default=None, min_length=8, max_length=200)


class InviteAccept(BaseModel):
    display_name: str = Field(min_length=2, max_length=120)
    access_key: str | None = None


class TransferProject(BaseModel):
    target_user_id: int
    current_password: str


class MemberPermission(BaseModel):
    permission: str = Field(pattern="^(viewer|editor)$")


def _project_payload(project: Project, permission: str | None = None) -> dict:
    return {
        "id_project": project.id_project,
        "name": project.name,
        "description": project.description,
        "owner_id": project.owner_id,
        "archived": project.archived_at is not None,
        "guest_access_enabled": project.guest_access_enabled,
        "guest_key_required": project.guest_key_required,
        "permission": permission,
    }


def _owner_project(project_id: int, user: User, db: Session) -> Project:
    project = db.get(Project, project_id)
    if not project or (user.system_role != "superadmin" and project.owner_id != user.id_user):
        raise HTTPException(status_code=403, detail="Solo el propietario puede administrar este proyecto")
    return project


@router.post("")
def create_project(data: ProjectCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    project = Project(owner_id=user.id_user, name=data.name.strip(), description=data.description, guest_access_enabled=data.guest_access_enabled, guest_key_required=data.guest_key_required)
    db.add(project)
    db.flush()
    db.add(ProjectMembership(project_id=project.id_project, user_id=user.id_user, permission="owner"))
    db.commit()
    db.refresh(project)
    return _project_payload(project, "owner")


@router.get("")
def list_projects(include_archived: bool = False, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.system_role == "superadmin":
        query = db.query(Project)
        if not include_archived:
            query = query.filter(Project.archived_at.is_(None))
        return [_project_payload(project, "owner") for project in query.order_by(Project.name).all()]
    query = db.query(Project, ProjectMembership.permission).join(ProjectMembership, ProjectMembership.project_id == Project.id_project).filter(ProjectMembership.user_id == user.id_user)
    if not include_archived:
        query = query.filter(Project.archived_at.is_(None))
    return [_project_payload(project, permission) for project, permission in query.order_by(Project.name).all()]


@router.patch("/{project_id}")
def update_project(project_id: int, data: ProjectUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    project = _owner_project(project_id, user, db)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(project, key, value.strip() if isinstance(value, str) else value)
    db.commit()
    return _project_payload(project, "owner")


@router.delete("/{project_id}")
def archive_project(project_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    project = _owner_project(project_id, user, db)
    project.archived_at = datetime.utcnow()
    db.commit()
    return {"detail": "Proyecto archivado"}


@router.post("/{project_id}/restore")
def restore_project(project_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    project = _owner_project(project_id, user, db)
    project.archived_at = None
    db.commit()
    return _project_payload(project, "owner")


@router.post("/{project_id}/transfer")
def transfer_project(project_id: int, data: TransferProject, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    project = _owner_project(project_id, user, db)
    password_ok = guest_password_hasher.verify(user.password_hash, data.current_password)
    if not password_ok:
        raise HTTPException(status_code=400, detail="La contraseña actual no es correcta")
    target = db.get(User, data.target_user_id)
    if not target or not target.active:
        raise HTTPException(status_code=404, detail="Usuario destinatario no encontrado")
    old_membership = db.query(ProjectMembership).filter_by(project_id=project_id, user_id=user.id_user).first()
    target_membership = db.query(ProjectMembership).filter_by(project_id=project_id, user_id=target.id_user).first()
    if target_membership:
        target_membership.permission = "owner"
    else:
        db.add(ProjectMembership(project_id=project_id, user_id=target.id_user, permission="owner"))
    if old_membership:
        old_membership.permission = "editor"
    project.owner_id = target.id_user
    db.commit()
    return {"detail": "Propiedad transferida"}


@router.post("/{project_id}/invites")
def create_invite(project_id: int, data: InviteCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    project = _owner_project(project_id, user, db)
    if not project.guest_access_enabled:
        raise HTTPException(status_code=403, detail="Las invitaciones están desactivadas")
    if data.access_key and not project.guest_key_required:
        # A key may still be enabled for one invite without changing the project default.
        pass
    raw_token, token_hash = new_invite_token()
    invite = ProjectInvite(project_id=project_id, token_hash=token_hash, permission=data.permission, label=data.label, created_by=user.id_user, expires_at=(datetime.utcnow() + timedelta(hours=data.expires_in_hours)) if data.expires_in_hours else None)
    if data.access_key:
        invite.key_hash = guest_password_hasher.hash(data.access_key)
    db.add(invite)
    db.commit()
    return {"id_invite": invite.id_invite, "token": raw_token, "permission": invite.permission, "expires_at": invite.expires_at}


@router.get("/{project_id}/invites")
def list_invites(project_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _owner_project(project_id, user, db)
    return [{"id_invite": invite.id_invite, "permission": invite.permission, "label": invite.label, "expires_at": invite.expires_at, "revoked": invite.revoked_at is not None} for invite in db.query(ProjectInvite).filter_by(project_id=project_id).order_by(ProjectInvite.created_at.desc()).all()]


@router.post("/invites/{token}/accept")
def accept_invite(token: str, data: InviteAccept, response: Response, request: Request, db: Session = Depends(get_db)):
    invite = db.query(ProjectInvite).filter(ProjectInvite.token_hash == hash_token(token)).first()
    if not invite or invite.revoked_at or (invite.expires_at and invite.expires_at <= datetime.utcnow()):
        raise HTTPException(status_code=404, detail="La invitación no es válida o expiró")
    if invite.key_hash:
        if not data.access_key:
            raise HTTPException(status_code=401, detail="Este enlace requiere una clave")
        try:
            guest_password_hasher.verify(invite.key_hash, data.access_key)
        except (VerifyMismatchError, VerificationError):
            raise HTTPException(status_code=401, detail="La clave no es correcta")

    logged_user = None
    session_cookie = request.cookies.get("oh_session")
    if session_cookie:
        from app.models.user import UserSession
        user_session = db.query(UserSession).filter(UserSession.token_hash == hash_token(session_cookie)).first()
        if user_session and not user_session.revoked_at and user_session.expires_at > datetime.utcnow() and user_session.user.active:
            logged_user = user_session.user
            membership = db.query(ProjectMembership).filter_by(project_id=invite.project_id, user_id=logged_user.id_user).first()
            if membership is None:
                db.add(ProjectMembership(project_id=invite.project_id, user_id=logged_user.id_user, permission=invite.permission))
            elif membership.permission == "viewer" and invite.permission == "editor":
                membership.permission = "editor"

    session_token, session_hash = new_invite_token()
    expires_at = invite.expires_at or (datetime.utcnow() + timedelta(days=30))
    db.add(GuestSession(invite_id=invite.id_invite, token_hash=session_hash, display_name=data.display_name.strip(), expires_at=expires_at))
    db.commit()
    secure, samesite = cookie_settings()
    response.set_cookie(GUEST_COOKIE, session_token, max_age=max(1, int((expires_at - datetime.utcnow()).total_seconds())), httponly=True, secure=secure, samesite=samesite, path="/")
    return {"project": _project_payload(invite.project, invite.permission), "display_name": data.display_name.strip(), "permission": invite.permission, "linked_user": logged_user is not None}


@router.delete("/{project_id}/invites/{invite_id}")
def revoke_invite(project_id: int, invite_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _owner_project(project_id, user, db)
    invite = db.query(ProjectInvite).filter_by(id_invite=invite_id, project_id=project_id).first()
    if not invite:
        raise HTTPException(status_code=404, detail="Invitación no encontrada")
    invite.revoked_at = datetime.utcnow()
    db.commit()
    return {"detail": "Invitación revocada"}


@router.get("/{project_id}/members")
def list_members(project_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project or (user.system_role != "superadmin" and project.owner_id != user.id_user):
        raise HTTPException(status_code=403, detail="Solo el propietario puede administrar miembros")
    return [{"id_user": member.user.id_user, "name": member.user.name, "email": member.user.email, "permission": member.permission} for member in project.memberships]


@router.patch("/{project_id}/members/{user_id}")
def update_member_permission(project_id: int, user_id: int, data: MemberPermission, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _owner_project(project_id, user, db)
    membership = db.query(ProjectMembership).filter_by(project_id=project_id, user_id=user_id).first()
    if not membership:
        raise HTTPException(status_code=404, detail="El usuario no pertenece al proyecto")
    if membership.permission == "owner":
        raise HTTPException(status_code=400, detail="Transfiere la propiedad para cambiar al propietario")
    membership.permission = data.permission
    db.commit()
    return {"id_user": user_id, "permission": membership.permission}


@router.delete("/{project_id}/members/{user_id}")
def remove_member(project_id: int, user_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _owner_project(project_id, user, db)
    membership = db.query(ProjectMembership).filter_by(project_id=project_id, user_id=user_id).first()
    if not membership:
        raise HTTPException(status_code=404, detail="El usuario no pertenece al proyecto")
    if membership.permission == "owner":
        raise HTTPException(status_code=400, detail="No puedes eliminar al propietario")
    db.delete(membership)
    db.commit()
    return {"detail": "Miembro eliminado"}

