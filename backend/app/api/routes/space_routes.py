from fastapi import APIRouter, HTTPException
from fastapi import Depends
from sqlalchemy.orm import Session
from streamlit import status
from app.database.connection import get_db
from app.models.space import Space
from app.schemas.space import (SpaceCreate, SpaceResponse)

router = APIRouter(
    prefix="/spaces",
    tags=["Spaces"]
)

@router.get("/", response_model=list[SpaceResponse])
def get_spaces(
    db: Session = Depends(get_db)
):
    return db.query(Space).all()

@router.post("/", response_model=SpaceResponse)
def create_space(
    space: SpaceCreate,
    db: Session = Depends(get_db)
):
    new_space = Space(**space.model_dump())

    db.add(new_space)
    db.commit()
    db.refresh(new_space)

    return new_space

@router.get("/{space_id}", response_model=SpaceResponse)
def get_space(space_id: int, db: Session = Depends(get_db)):
    space = db.get(Space, space_id)

    if not space:
        raise HTTPException(
            status_code = 404,
            detail = "Space not found"
        )

    return space

@router.put("/{space_id}", response_model=SpaceResponse)
def update_space(space_id: int, space_data: SpaceCreate, db: Session = Depends(get_db)):
    space = db.get(Space, space_id)

    if not space:
        raise HTTPException(
            status_code = 404,
            detail = "Space not found"
        )

    space.name = space_data.name
    space.capacity = space_data.capacity

    db.commit()
    db.refresh(space)

    return space

@router.delete("/{space_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_space(space_id: int, db: Session = Depends(get_db)):
    space = db.get(Space, space_id)

    if not space:
        raise HTTPException(
            status_code = 404,
            detail = "Space not found"
        )

    db.delete(space)
    db.commit()

    return {"detail": "Space deleted successfully"}