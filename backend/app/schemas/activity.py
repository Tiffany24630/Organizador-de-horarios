from pydantic import BaseModel
from sqlalchemy import UniqueConstraint


class ActivityCreate(BaseModel):
    __table_args__ = UniqueConstraint("group_id", "person_id", name="uq_group_person"),

    person_id: int
    name: str
    type: str
    description: str | None = None

class ActivityUpdate(BaseModel):
    person_id: int | None = None
    name: str | None = None
    type: str | None = None
    description: str | None = None

class ActivityResponse(BaseModel):
    id_activity: int
    person_id: int
    name: str
    type: str
    description: str | None

    model_config = {
        "from_attributes": True
    }