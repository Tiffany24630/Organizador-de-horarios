from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.accepted_schedule import AcceptedSchedule

router = APIRouter(prefix="/accepted-schedules", tags=["Accepted Schedules"])

@router.get("/")
def get_all(db: Session = Depends(get_db)):
    return db.query(AcceptedSchedule).all()