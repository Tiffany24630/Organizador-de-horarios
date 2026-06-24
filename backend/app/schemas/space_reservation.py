from datetime import time
from pydantic import BaseModel
from app.models.enums import DayOfWeek
from pydantic import model_validator

class SpaceReservationCreate(BaseModel):
    space_id: int
    day_of_week: DayOfWeek
    start_time: time
    end_time: time

    description: str | None = None

    @model_validator(mode="after")
    def validate_times(self):
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be greater than start_time")

        return self

class SpaceReservationResponse(BaseModel):
    id_reservation: int
    space_id: int
    day_of_week: DayOfWeek
    start_time: time
    end_time: time

    class Config:
        from_attributes = True