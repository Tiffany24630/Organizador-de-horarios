from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.time_block import TimeBlock
from app.models.activity import Activity
from app.schemas.time_block import (TimeBlockCreate, TimeBlockUpdate, TimeBlockResponse)

router = APIRouter(prefix="/time-blocks", tags=["Time Blocks"])

@router.get("/", response_model=list[TimeBlockResponse])
def get_blocks(
    db: Session = Depends(get_db)
):
    return db.query(TimeBlock).all()


@router.get("/{block_id}", response_model=TimeBlockResponse)
def get_block(block_id: int, db: Session = Depends(get_db)):
    block = db.get(TimeBlock, block_id)

    if not block:
        raise HTTPException(
            status_code=404,
            detail="Block not found"
        )

    return block


@router.post("/", response_model=TimeBlockResponse)
def create_block(block: TimeBlockCreate, db: Session = Depends(get_db)):
    activity = db.get(Activity, block.activity_id)

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


@router.put("/{block_id}")
def update_block(block_id: int, block_data: TimeBlockUpdate, db: Session = Depends(get_db)):
    block = db.get(TimeBlock, block_id)

    if not block:
        raise HTTPException(
            status_code=404,
            detail="Block not found"
        )

    block.day_of_week = block_data.day_of_week
    block.start_time = block_data.start_time
    block.end_time = block_data.end_time

    db.commit()
    db.refresh(block)

    return block


@router.delete("/{block_id}")
def delete_block(block_id: int, db: Session = Depends(get_db)):
    block = db.get(TimeBlock, block_id)

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