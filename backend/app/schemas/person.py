from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import ConfigDict

class PersonCreate(BaseModel):
    name: str
    email: EmailStr

    model_config = ConfigDict(
        json_encoders={
            "example": {
                "name": "Juan Pérez",
                "email": "juan@email.com"
            }
        }
    )

class PersonUpdate(BaseModel):
    name: str 
    email: EmailStr 
    active: bool

class PersonResponse(BaseModel):
    id_person: int
    name: str
    email: str
    active: bool

    model_config = {
        "from_attributes": True
    }