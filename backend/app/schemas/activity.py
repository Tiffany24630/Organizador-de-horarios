from pydantic import BaseModel

class ActivityCreate(BaseModel):
    person_id: int
    name: str
    type: str
    description: str | None = None

class ActivityUpdate(BaseModel):
    person_id: int
    name: str
    type: str
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