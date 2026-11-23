import json
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.proposal_attendance import ProposalAttendance
from app.models.proposed_schedule import ProposedSchedule
from app.models.activity_group import ActivityGroup
from app.core.project_access import ProjectAccess, require_project_access

router = APIRouter(prefix="/proposal-attendance", tags=["Proposal Attendance"])

@router.get("/proposal/{proposal_id}")
def get_attendance(proposal_id: int, context: ProjectAccess = Depends(require_project_access), db: Session = Depends(get_db)):
    if not db.query(ProposedSchedule).join(ActivityGroup).filter(ProposedSchedule.id_schedule == proposal_id, ActivityGroup.project_id == context.project_id).first():
        raise HTTPException(status_code=404, detail="Proposal not found")
    return [{
        "id_attendance": item.id_attendance,
        "proposal_id": item.proposal_id,
        "person_id": item.person_id,
        "name": item.person.name if item.person else f"Persona {item.person_id}",
        "can_attend": item.can_attend,
        "available_minutes": item.available_minutes,
        "reason": item.reason,
        "conflicts": json.loads(item.conflicts_json or "[]"),
    } for item in db.query(ProposalAttendance).filter(ProposalAttendance.proposal_id == proposal_id).all()]
