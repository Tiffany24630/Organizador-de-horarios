from pydantic import BaseModel

class ProposalResponse(BaseModel):
    id_schedule: int
    group_id: int
    name: str
    attendance_percentage: float
    score: float
    status: str

    class Config:
        from_attributes = True