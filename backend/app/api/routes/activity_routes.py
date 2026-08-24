from fastapi import APIRouter, HTTPException
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.activity import Activity
from app.models.person import Person
from app.schemas.activity import ActivityCreate, ActivityUpdate, ActivityResponse

router = APIRouter(prefix="/activities", tags=["Activities"])

@router.get("/", response_model=list[ActivityResponse])
def get_activities(
    person_id: int | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(Activity)
    if person_id is not None:
        query = query.filter(Activity.person_id == person_id)
    return query.all()

@router.post("/", response_model=ActivityResponse)
def create_activity(
    activity: ActivityCreate,
    db: Session = Depends(get_db)
):
    if not db.get(Person, activity.person_id):
        raise HTTPException(status_code=404, detail="Person not found")
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
def update_activity(activity_id: int, activity_data: ActivityUpdate, db: Session = Depends(get_db)):
    activity = db.get(Activity, activity_id)

    if not activity:
        raise HTTPException(
            status_code = 404,
            detail = "Activity not found"
        )

    for key, value in activity_data.model_dump(exclude_unset=True).items():
        setattr(activity, key, value)

    db.commit()
    db.refresh(activity)

    return activity

@router.delete("/{activity_id}", status_code=200)
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
