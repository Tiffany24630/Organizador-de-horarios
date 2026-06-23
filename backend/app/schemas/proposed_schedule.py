from pydantic import BaseModel
from app.models.enums import ProposalStatus

class ProposalResponse(BaseModel):
    id_schedule: int
    group_id: int
    name: str
    attendance_percentage: float
    score: float
    status: ProposalStatus

    class Config:
        from_attributes = True