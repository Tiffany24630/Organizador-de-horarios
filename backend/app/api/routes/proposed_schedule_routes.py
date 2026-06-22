from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.proposed_schedule import ProposedSchedule
from app.models.enums import ProposalStatus
from app.schemas.proposed_schedule import ProposalResponse

router = APIRouter(prefix="/proposal-schedules", tags=["Proposal Schedules"])

@router.get("/", response_model=list[ProposalResponse])
def get_proposals(db: Session = Depends(get_db)):
    return db.query(ProposedSchedule).all()

@router.get("/{proposal_id}", response_model=ProposalResponse)
def get_proposal(proposal_id: int, db: Session = Depends(get_db)):
    proposal = db.get(ProposedSchedule, proposal_id)

    if not proposal:
        raise HTTPException(404, "Proposal not found")

    return proposal

@router.put("/{proposal_id}/accept")
def accept_proposal(proposal_id: int, db: Session = Depends(get_db)):
    proposal = db.get(ProposedSchedule, proposal_id)

    if not proposal:
        raise HTTPException(404, "Proposal not found")

    proposal.status = ProposalStatus.ACCEPTED

    db.commit()

    return {
        "message": "Proposal accepted"
    }

@router.put("/{proposal_id}/reject")
def reject_proposal(proposal_id: int, db: Session = Depends(get_db)):
    proposal = db.get(ProposedSchedule, proposal_id)

    if not proposal:
        raise HTTPException(404, "Proposal not found")

    proposal.status = ProposalStatus.REJECTED

    db.commit()

    return {
        "message": "Proposal rejected"
    }
