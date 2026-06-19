from pydantic import BaseModel

class SpaceCreate(BaseModel):
    name: str
    capacity: int

class SpaceResponse(BaseModel):
    id_space: int
    name: str
    capacity: int

    model_config = {
        "from_attributes": True
    }