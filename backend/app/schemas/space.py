from pydantic import BaseModel
from pydantic import Field

class SpaceCreate(BaseModel):
    name: str
    capacity: int = Field(gt=0)

class SpaceUpdate(BaseModel):
    name: str
    capacity: int

class SpaceResponse(BaseModel):
    id_space: int
    name: str
    capacity: int

    model_config = {
        "from_attributes": True
    }