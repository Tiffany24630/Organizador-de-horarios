from pydantic import BaseModel
from sqlalchemy import UniqueConstraint

class GroupParticipantCreate(BaseModel):
    __table_args__ = UniqueConstraint("group_id", "person_id", name="uq_group_person"),

    group_id: int
    person_id: int
    
    required: bool = True

class GroupParticipantResponse(BaseModel):
    id_participant: int
    group_id: int
    person_id: int
    required: bool

    class Config:
        from_attributes = True