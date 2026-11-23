from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.time_block import TimeBlock
from app.models.activity import Activity
from app.models.person import Person
from app.core.project_access import ProjectAccess, require_project_access
from app.schemas.time_block import TimeBlockCreate, TimeBlockUpdate, TimeBlockEdit, TimeBlockResponse

router = APIRouter(prefix="/time-blocks", tags=["Time Blocks"])

@router.get("/", response_model=list[TimeBlockResponse])
def get_blocks(person_id: int | None = None, activity_id: int | None = None, context: ProjectAccess = Depends(require_project_access), db: Session = Depends(get_db)):
    query = db.query(TimeBlock).join(Activity).join(Person).filter(Person.project_id == context.project_id)
    if person_id is not None:
        query = query.join(Activity).filter(Activity.person_id == person_id)
    if activity_id is not None:
        query = query.filter(TimeBlock.activity_id == activity_id)
    return query.all()


@router.get("/{block_id}", response_model=TimeBlockResponse)
def get_block(block_id: int, context: ProjectAccess = Depends(require_project_access), db: Session = Depends(get_db)):
    block = db.query(TimeBlock).join(Activity).join(Person).filter(TimeBlock.id_block == block_id, Person.project_id == context.project_id).first()

    if not block:
        raise HTTPException(
            status_code=404,
            detail="Block not found"
        )

    return block


@router.post("/", response_model=TimeBlockResponse)
def create_block(block: TimeBlockCreate, context: ProjectAccess = Depends(require_project_access), db: Session = Depends(get_db)):
    activity = db.query(Activity).join(Person).filter(Activity.id_activity == block.activity_id, Person.project_id == context.project_id).first()

    if not activity:
        raise HTTPException(
            status_code=404,
            detail="Activity not found"
        )

    new_block = TimeBlock(**block.model_dump())

    db.add(new_block)
    db.commit()
    db.refresh(new_block)

    return new_block


@router.put("/{block_id}/edit", response_model=TimeBlockResponse)
def edit_block(block_id: int, block_data: TimeBlockEdit, context: ProjectAccess = Depends(require_project_access), db: Session = Depends(get_db)):
    block = db.query(TimeBlock).join(Activity).join(Person).filter(TimeBlock.id_block == block_id, Person.project_id == context.project_id).first()

    if not block:
        raise HTTPException(
            status_code=404,
            detail="Block not found"
        )

    activity = db.get(Activity, block.activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    try:
        activity.name = block_data.activity_name.strip()
        block.day_of_week = block_data.day_of_week
        block.start_time = block_data.start_time
        block.end_time = block_data.end_time
        block.room = block_data.room
        db.commit()
        db.refresh(block)
        return block
    except Exception:
        db.rollback()
        raise


@router.put("/{block_id}", response_model=TimeBlockResponse)
def update_block(block_id: int, block_data: TimeBlockUpdate, context: ProjectAccess = Depends(require_project_access), db: Session = Depends(get_db)):
    block = db.query(TimeBlock).join(Activity).join(Person).filter(TimeBlock.id_block == block_id, Person.project_id == context.project_id).first()
    if not block:
        raise HTTPException(status_code=404, detail="Block not found")
    changes = block_data.model_dump(exclude_unset=True)
    block.day_of_week = changes["day_of_week"]
    block.start_time = changes["start_time"]
    block.end_time = changes["end_time"]
    if "room" in changes:
        block.room = changes["room"]
    db.commit()
    db.refresh(block)
    return block


@router.delete("/{block_id}")
def delete_block(block_id: int, context: ProjectAccess = Depends(require_project_access), db: Session = Depends(get_db)):
    block = db.query(TimeBlock).join(Activity).join(Person).filter(TimeBlock.id_block == block_id, Person.project_id == context.project_id).first()

    if not block:
        raise HTTPException(
            status_code=404,
            detail="Block not found"
        )

    db.delete(block)
    db.commit()

    return {
        "message": "Block deleted"
    }
