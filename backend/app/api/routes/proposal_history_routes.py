from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.proposal_history import ProposalHistory
from app.models.proposed_schedule import ProposedSchedule
from app.models.activity_group import ActivityGroup
from app.core.project_access import ProjectAccess, require_project_access
from app.schemas.proposal_history import ProposalHistoryResponse

router = APIRouter(prefix="/proposal-history", tags=["Proposal History"])

@router.get("/{proposal_id}", response_model=list[ProposalHistoryResponse])
def get_history(proposal_id: int, context: ProjectAccess = Depends(require_project_access), db: Session = Depends(get_db)):
    return db.query(ProposalHistory).join(ProposedSchedule).join(ActivityGroup).filter(ProposalHistory.proposal_id == proposal_id, ActivityGroup.project_id == context.project_id).all()
