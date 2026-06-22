from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.proposal_history import ProposalHistory
from app.schemas.proposal_history import ProposalHistoryResponse

router = APIRouter(prefix="/proposal-history", tags=["Proposal History"])

@router.get("/{proposal_id}", response_model=list[ProposalHistoryResponse])
def get_history(proposal_id: int, db: Session = Depends(get_db)):
    return db.query(ProposalHistory).filter(ProposalHistory.proposal_id == proposal_id).all()