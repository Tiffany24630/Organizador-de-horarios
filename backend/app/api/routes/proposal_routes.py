from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.database.connection import get_db
from app.models.proposed_session import ProposedSession
from app.services.proposal_management_service import accept_proposal
from app.services.proposal_generator_service import generate_proposals

router = APIRouter(prefix = "/proposals", tags = ["Proposals"])

@router.post("/generate/{group_id}")
def generate(group_id: int, db: Session = Depends(get_db)):
    return generate_proposals(group_id, db)

@router.put("/{proposal_id}/accept")
def accept(proposal_id: int, db: Session = Depends(get_db)):
    proposal = db.get(ProposedSchedule, proposal_id)

    if not proposal:
        raise HTTPException(404, "Proposal not found")

    accept_proposal(proposal, db)

    return {
        "message": "Proposal accepted"
    }

