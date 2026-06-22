from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.proposed_session import ProposedSession
from app.schemas.proposed_session import ProposedSessionResponse

router = APIRouter(prefix="/proposal-sessions", tags=["Proposal Sessions"])

@router.get("/{schedule_id}", response_model=list[ProposedSessionResponse])
def get_sessions(schedule_id: int, db: Session = Depends(get_db)):
    return (db.query(ProposedSession).filter(ProposedSession.schedule_id == schedule_id).all())