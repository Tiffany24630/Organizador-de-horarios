from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
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