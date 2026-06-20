from pydantic import BaseModel

class GroupParticipantCreate(BaseModel):
    group_id: int
    person_id: int
    required: bool = True

class GroupParticipantResponse(GroupParticipantCreate):
    id_participant: int

    model_config = {
        "from_attributes": True
    }