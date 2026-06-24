from datetime import time
from pydantic import BaseModel
from app.models.enums import RestrictionType, DayOfWeek
from sqlalchemy import UniqueConstraint

class RestrictionCreate(BaseModel):
    __table_args__ = UniqueConstraint("group_id", "name", name="uq_group_restriction"),
    
    group_id: int
    name: str

    description: str | None = None

    type: RestrictionType

    day_of_week: DayOfWeek | None = None
    start_time: time | None = None
    end_time: time | None = None

class RestrictionResponse(BaseModel):
    id_restriction: int
    group_id: int
    name: str
    type: RestrictionType

    class Config:
        from_attributes = True