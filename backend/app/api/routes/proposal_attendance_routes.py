from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.proposal_attendance import ProposalAttendance
from app.schemas.proposal_attendance import ProposalAttendanceResponse

router = APIRouter(prefix="/proposal-attendance", tags=["Proposal Attendance"])

@router.get("/proposal/{proposal_id}", response_model=list[ProposalAttendanceResponse])
def get_attendance(proposal_id: int, db: Session = Depends(get_db)):
    return (db.query(ProposalAttendance).filter(ProposalAttendance.proposal_id == proposal_id).all())

