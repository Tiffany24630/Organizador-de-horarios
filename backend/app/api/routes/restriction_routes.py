from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.restriction import Restriction
from app.schemas.restriction import (RestrictionCreate, RestrictionResponse)

router = APIRouter(prefix="/restrictions", tags=["Restrictions"])

@router.post("/", response_model=RestrictionResponse)
def create_restriction(data: RestrictionCreate, db: Session = Depends(get_db)):
    restriction = Restriction(**data.model_dump())

    db.add(restriction)
    db.commit()
    db.refresh(restriction)

    return restriction

@router.get("/", response_model=list[RestrictionResponse])
def get_restrictions(db: Session = Depends(get_db)):
    return db.query(Restriction).all()

@router.get("/{restriction_id}", response_model=RestrictionResponse)
def get_restriction(restriction_id: int, db: Session = Depends(get_db)):
    restriction = db.get(Restriction, restriction_id)

    if not restriction:
        raise HTTPException(status_code=404, detail="Restriction not found")

    return restriction

@router.delete("/{restriction_id}")
def delete_restriction(restriction_id: int, db: Session = Depends(get_db)):
    restriction = db.get(Restriction, restriction_id)

    if not restriction:
        raise HTTPException(status_code=404, detail="Restriction not found")

    db.delete(restriction)
    db.commit()

    return {
        "message": "Restriction deleted"
    }