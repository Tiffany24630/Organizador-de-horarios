from pydantic import BaseModel
from pydantic import EmailStr

class PersonCreate(BaseModel):
    name: str
    email: EmailStr

class PersonResponse(BaseModel):
    id_person: int
    name: str
    email: str
    active: bool

    model_config = {
        "from_attributes": True
    }