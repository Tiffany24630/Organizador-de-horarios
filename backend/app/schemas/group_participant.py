from pydantic import BaseModel

class GroupParticipantCreate(BaseModel):
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