from pydantic import BaseModel
from datetime import time
from app.models.enums import DayOfWeek

class TimeBlockCreate(BaseModel):
    activity_id: int
    day_of_week: DayOfWeek
    start_time: time
    end_time: time

class TimeBlockUpdate(BaseModel):
    day_of_week: DayOfWeek
    start_time: time
    end_time: time

class TimeBlockResponse(BaseModel):
    id_block: int
    activity_id: int
    day_of_week: DayOfWeek
    start_time: time
    end_time: time

    model_config = {
        "from_attributes": True
    }