from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.space_reservation import SpaceReservation
from app.schemas.space_reservation import SpaceReservationCreate, SpaceReservationResponse

router = APIRouter(prefix="/space-reservations", tags=["Space Reservations"])

@router.post("/", response_model=SpaceReservationResponse)
def create_reservation(data: SpaceReservationCreate, db: Session = Depends(get_db)):
    reservation = SpaceReservation(**data.model_dump())

    db.add(reservation)
    db.commit()
    db.refresh(reservation)

    return reservation

@router.get("/", response_model=list[SpaceReservationResponse])
def get_reservations(db: Session = Depends(get_db)):
    return db.query(SpaceReservation).all()

@router.get("/{reservation_id}", response_model=SpaceReservationResponse)
def get_reservation(reservation_id: int, db: Session = Depends(get_db)):
    reservation = db.get(SpaceReservation, reservation_id)

    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")

    return reservation

@router.delete("/{reservation_id}")
def delete_reservation(reservation_id: int, db: Session = Depends(get_db)):
    reservation = db.get(SpaceReservation, reservation_id)

    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")

    db.delete(reservation)
    db.commit()

    return {
        "message": "Reservation deleted"
    }