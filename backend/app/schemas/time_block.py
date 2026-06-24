from pydantic import BaseModel
from datetime import time
from app.models.enums import DayOfWeek
from pydantic import model_validator

class TimeBlockCreate(BaseModel):
    activity_id: int
    day_of_week: DayOfWeek
    start_time: time
    end_time: time

    @model_validator(mode="after")
    def validate_times(self):
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be greater than start_time")

        return self

class TimeBlockUpdate(BaseModel):
    day_of_week: DayOfWeek
    start_time: time
    end_time: time

    @model_validator(mode="after")
    def validate_times(self):
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be greater than start_time")

        return self

class TimeBlockResponse(BaseModel):
    id_block: int
    activity_id: int
    day_of_week: DayOfWeek
    start_time: time
    end_time: time

    model_config = {
        "from_attributes": True
    }