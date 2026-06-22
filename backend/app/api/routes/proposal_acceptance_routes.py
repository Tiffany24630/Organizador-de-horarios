from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.services.proposal_acceptance_service import accept_proposal, reject_proposal

router = APIRouter(prefix="/proposal-actions", tags=["Proposal Actions"])

@router.post("/accept/{proposal_id}")
def accept(proposal_id: int, db: Session = Depends(get_db)):
    return accept_proposal(proposal_id, db)

@router.post("/reject/{proposal_id}")
def reject(proposal_id: int, db: Session = Depends(get_db)):
    return reject_proposal(proposal_id, db)