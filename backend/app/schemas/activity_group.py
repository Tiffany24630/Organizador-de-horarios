from datetime import date
from pydantic import BaseModel
from pydantic import Field

class ActivityGroupCreate(BaseModel):
    name: str
    description: str | None = None
    sessions_per_week: int
    duration_minutes: int
    minimum_attendance_minutes: int
    start_date: date | None = None
    end_date: date | None = None
    sessions_per_week: int = Field(gt=0)
    duration_minutes: int = Field(gt=0)
    minimum_attendance_minutes: int = Field(gt=0)

class ActivityGroupUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    sessions_per_week: int | None = None
    duration_minutes: int | None = None
    minimum_attendance_minutes: int | None = None
    start_date: date | None = None
    end_date: date | None = None
    active: bool | None = None

class ActivityGroupResponse(BaseModel):
    id_group: int
    name: str
    description: str | None
    sessions_per_week: int
    duration_minutes: int
    minimum_attendance_minutes: int
    active: bool

    class Config:
        from_attributes = True