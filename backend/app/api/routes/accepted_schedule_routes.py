from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.accepted_schedule import AcceptedSchedule
from app.models.proposed_schedule import ProposedSchedule
from app.models.activity_group import ActivityGroup
from app.core.project_access import ProjectAccess, require_project_access

router = APIRouter(prefix="/accepted-schedules", tags=["Accepted Schedules"])

@router.get("/")
def get_all(context: ProjectAccess = Depends(require_project_access), db: Session = Depends(get_db)):
    return db.query(AcceptedSchedule).join(ProposedSchedule).join(ActivityGroup).filter(ActivityGroup.project_id == context.project_id).all()
