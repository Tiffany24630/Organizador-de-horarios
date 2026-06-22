from pydantic import BaseModel

class ProposedSessionResponse(BaseModel):
    id_session: int
    schedule_id: int
    day_of_week: str
    start_time: str
    end_time: str

    class Config:
        from_attributes = True