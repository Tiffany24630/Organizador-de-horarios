import json
from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.proposal_attendance import ProposalAttendance

router = APIRouter(prefix="/proposal-attendance", tags=["Proposal Attendance"])

@router.get("/proposal/{proposal_id}")
def get_attendance(proposal_id: int, db: Session = Depends(get_db)):
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
