from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.database.connection import get_db
from app.models.proposed_schedule import ProposedSchedule
from app.services.proposal_management_service import reject_proposal
from app.services.proposal_management_service import accept_proposal
from app.services.proposal_generator_service import generate_proposals

router = APIRouter(prefix = "/proposals", tags = ["Proposals"])

@router.post("/generate/{group_id}")
def generate(group_id: int, db: Session = Depends(get_db)):
    try:
        return generate_proposals(group_id, db)
    except ValueError as error:
        raise HTTPException(400, str(error)) from error

@router.put("/{proposal_id}/accept")
def accept(proposal_id: int, db: Session = Depends(get_db)):
    proposal = db.get(ProposedSchedule, proposal_id)

    if not proposal:
        raise HTTPException(404, "Proposal not found")

    accept_proposal(proposal, db)

    return {
        "message": "Proposal accepted"
    }

@router.get("/")
def get_proposals(db: Session = Depends(get_db)):
    return db.query(ProposedSchedule).all()


@router.get("/{proposal_id}")
def get_proposal(proposal_id: int, db: Session = Depends(get_db)):
    proposal = db.get(ProposedSchedule, proposal_id)

    if not proposal:
        raise HTTPException(404, "Proposal not found")

    return {
        "id_schedule": proposal.id_schedule,
        "group_id": proposal.group_id,
        "name": proposal.name,
        "attendance_percentage": proposal.attendance_percentage,
        "score": proposal.score,
        "status": proposal.status,
        "sessions": proposal.sessions,
        "attendances": proposal.attendances,
    }

@router.put("/{proposal_id}/reject")
def reject(proposal_id: int, db: Session = Depends(get_db)):
    proposal = db.get(ProposedSchedule, proposal_id)

    if not proposal:
        raise HTTPException(404, "Proposal not found")

    reject_proposal(proposal, db)

    return {
        "message": "Proposal rejected"
    }
