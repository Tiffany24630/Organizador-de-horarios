from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.person import Person
from app.models.activity import Activity
from app.models.activity_group import ActivityGroup
from app.models.proposed_schedule import ProposedSchedule

router = APIRouter(prefix="/statistics", tags=["Statistics"])

@router.get("/")
def statistics(db: Session = Depends(get_db)):
    return {
        "people": db.query(Person).count(),
        "activities": db.query(Activity).count(),
        "groups": db.query(ActivityGroup).count(),
        "proposals": db.query(ProposedSchedule).count()
    }