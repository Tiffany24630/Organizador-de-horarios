from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.proposed_session import ProposedSession
from app.models.proposed_schedule import ProposedSchedule
from app.models.activity_group import ActivityGroup
from app.core.project_access import ProjectAccess, require_project_access
from app.schemas.proposed_session import ProposedSessionResponse

router = APIRouter(prefix="/proposal-sessions", tags=["Proposal Sessions"])

@router.get("/{schedule_id}", response_model=list[ProposedSessionResponse])
def get_sessions(schedule_id: int, context: ProjectAccess = Depends(require_project_access), db: Session = Depends(get_db)):
    return (db.query(ProposedSession).join(ProposedSchedule).join(ActivityGroup).filter(ProposedSession.schedule_id == schedule_id, ActivityGroup.project_id == context.project_id).all())
