from fastapi import APIRouter, HTTPException
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

@router.get("/{activity_id}", response_model=ActivityResponse)
def get_activity(activity_id: int, db: Session = Depends(get_db)):
    activity = db.get(Activity, activity_id)

    if not activity:
        raise HTTPException(
            status_code = 404,
            detail = "Activity not found"
        )

    return activity

@router.put("/{activity_id}", response_model=ActivityResponse)
def update_activity(activity_id: int, activity_data: ActivityCreate, db: Session = Depends(get_db)):
    activity = db.get(Activity, activity_id)

    if not activity:
        raise HTTPException(
            status_code = 404,
            detail = "Activity not found"
        )

    activity.person_id = activity_data.person_id
    activity.name = activity_data.name
    activity.type = activity_data.type
    activity.description = activity_data.description

    db.commit()
    db.refresh(activity)

    return activity

@router.delete("/{activity_id}", status_code=204)
def delete_activity(activity_id: int, db: Session = Depends(get_db)):
    activity = db.get(Activity, activity_id)

    if not activity:
        raise HTTPException(
            status_code = 404,
            detail = "Activity not found"
        )

    db.delete(activity)
    db.commit()

    return {"detail": "Activity deleted successfully"}