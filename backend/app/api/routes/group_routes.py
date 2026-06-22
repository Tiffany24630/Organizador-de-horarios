from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.activity_group import ActivityGroup
from app.schemas.activity_group import ActivityGroupCreate, ActivityGroupUpdate, ActivityGroupResponse

router = APIRouter(prefix="/groups", tags=["Groups"])

@router.post("/", response_model=ActivityGroupResponse)
def create_group(group: ActivityGroupCreate, db: Session = Depends(get_db)):
    new_group = ActivityGroup(**group.model_dump())

    db.add(new_group)
    db.commit()
    db.refresh(new_group)

    return new_group

@router.get("/", response_model=list[ActivityGroupResponse])
def get_groups(db: Session = Depends(get_db)):
    return db.query(ActivityGroup).all()

@router.get("/{group_id}", response_model=ActivityGroupResponse)
def get_group(group_id: int, db: Session = Depends(get_db)):
    group = db.get(ActivityGroup, group_id)

    if not group:
        raise HTTPException(404, "Group not found")

    return group

@router.put("/{group_id}", response_model=ActivityGroupResponse)
def update_group(group_id: int, data: ActivityGroupUpdate, db: Session = Depends(get_db)):
    group = db.get(ActivityGroup, group_id)

    if not group:
        raise HTTPException(404, "Group not found")

    for key, value in (data.model_dump(exclude_unset=True).items()): 
        setattr(group, key, value)

    db.commit()
    db.refresh(group)

    return group

@router.delete("/{group_id}")
def delete_group(group_id: int, db: Session = Depends(get_db)):
    group = db.get(ActivityGroup, group_id)

    if not group:
        raise HTTPException(404, "Group not found")

    db.delete(group)
    db.commit()

    return {
        "message":
        "Group deleted"
    }