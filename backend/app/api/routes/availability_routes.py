from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.services.availability_matrix_service import (build_matrix)
from app.services.availability_service import (build_group_availability)

router = APIRouter(prefix="/availability", tags=["Availability"])

@router.get("/{group_id}")
def get_availability(group_id: int, db: Session = Depends(get_db)):
    return build_group_availability(group_id, db)

@router.get("/matrix/{group_id}")
def availability_matrix(group_id: int, db: Session = Depends(get_db)):
    return build_matrix(group_id, db)