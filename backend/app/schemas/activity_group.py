from datetime import date
from pydantic import BaseModel
from sqlalchemy.orm import relationship

class ActivityGroupCreate(BaseModel):
    name: str

    description: str | None = None

    sessions_per_week: int
    duration_minutes: int
    minimum_attendance_minutes: int

    start_date: date | None = None
    end_date: date | None = None

    schedules = relationship("ProposedSchedule", cascade="all, delete-orphan")

class ActivityGroupResponse(ActivityGroupCreate):
    id_group: int
    active: bool

    model_config = {
        "from_attributes": True
    }