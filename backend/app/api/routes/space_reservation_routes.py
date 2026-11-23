from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.space_reservation import SpaceReservation
from app.schemas.space_reservation import SpaceReservationCreate, SpaceReservationResponse
from app.models.space import Space
from app.core.project_access import ProjectAccess, require_project_access

router = APIRouter(prefix="/space-reservations", tags=["Space Reservations"])

@router.post("/", response_model=SpaceReservationResponse)
def create_reservation(data: SpaceReservationCreate, context: ProjectAccess = Depends(require_project_access), db: Session = Depends(get_db)):
    if not db.query(Space).filter(Space.id_space == data.space_id, Space.project_id == context.project_id).first():
        raise HTTPException(status_code=404, detail="Space not found")
    reservation = SpaceReservation(**data.model_dump())

    db.add(reservation)
    db.commit()
    db.refresh(reservation)

    return reservation

@router.get("/", response_model=list[SpaceReservationResponse])
def get_reservations(context: ProjectAccess = Depends(require_project_access), db: Session = Depends(get_db)):
    return db.query(SpaceReservation).join(Space).filter(Space.project_id == context.project_id).all()

@router.get("/{reservation_id}", response_model=SpaceReservationResponse)
def get_reservation(reservation_id: int, context: ProjectAccess = Depends(require_project_access), db: Session = Depends(get_db)):
    reservation = db.query(SpaceReservation).join(Space).filter(SpaceReservation.id_reservation == reservation_id, Space.project_id == context.project_id).first()

    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")

    return reservation

@router.delete("/{reservation_id}")
def delete_reservation(reservation_id: int, context: ProjectAccess = Depends(require_project_access), db: Session = Depends(get_db)):
    reservation = db.query(SpaceReservation).join(Space).filter(SpaceReservation.id_reservation == reservation_id, Space.project_id == context.project_id).first()

    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")

    db.delete(reservation)
    db.commit()

    return {
        "message": "Reservation deleted"
    }
