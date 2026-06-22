from datetime import time
from pydantic import BaseModel
from app.models.enums import DayOfWeek

class SpaceReservationCreate(BaseModel):
    space_id: int
    day_of_week: DayOfWeek
    start_time: time
    end_time: time

    description: str | None = None

class SpaceReservationResponse(BaseModel):
    id_reservation: int
    space_id: int
    day_of_week: DayOfWeek
    start_time: time
    end_time: time

    class Config:
        from_attributes = True