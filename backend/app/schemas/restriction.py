from datetime import time
from pydantic import BaseModel
from app.models.enums import RestrictionType, DayOfWeek
from pydantic import model_validator

class RestrictionCreate(BaseModel):
    group_id: int
    name: str

    description: str | None = None

    type: RestrictionType

    day_of_week: DayOfWeek | None = None
    start_time: time | None = None
    end_time: time | None = None

    @model_validator(mode="after")
    def validate_restriction(self):
        if self.type == RestrictionType.FORBIDDEN_DAY:
            if self.day_of_week is None:
                raise ValueError("FORBIDDEN_DAY requires day_of_week")

        elif self.type in (RestrictionType.ALLOWED_HOURS, RestrictionType.FORBIDDEN_HOURS):
            if self.start_time is None or self.end_time is None:
                raise ValueError("Hour restrictions require start_time and end_time")

            if self.end_time <= self.start_time:
                raise ValueError("end_time must be greater than start_time")

        return self

class RestrictionResponse(BaseModel):
    id_restriction: int
    group_id: int
    name: str
    type: RestrictionType

    class Config:
        from_attributes = True