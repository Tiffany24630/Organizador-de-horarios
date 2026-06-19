from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.activity import Activity
from app.schemas.activity import (ActivityCreate, ActivityResponse)

router = APIRouter(
    prefix="/activities",
    tags=["Activities"]
)

@router.get("/", response_model=list[ActivityResponse])
def get_activities(
    db: Session = Depends(get_db)
):
    return db.query(Activity).all()

@router.post("/", response_model=ActivityResponse)
def create_activity(
    activity: ActivityCreate,
    db: Session = Depends(get_db)
):
    new_activity = Activity(**activity.model_dump())

    db.add(new_activity)
    db.commit()
    db.refresh(new_activity)

    return new_activity