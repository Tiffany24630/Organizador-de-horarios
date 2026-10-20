from pydantic import BaseModel
from app.models.enums import ProposalStatus

class ProposalResponse(BaseModel):
    id_schedule: int
    group_id: int
    name: str
    attendance_percentage: float
    score: float
    attending_count: int = 0
    total_people: int = 0
    explanation: str | None = None
    status: ProposalStatus

    class Config:
        from_attributes = True
