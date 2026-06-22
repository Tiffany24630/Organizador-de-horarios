from pydantic import BaseModel

class ProposalAttendanceResponse(BaseModel):
    id_attendance: int
    proposal_id: int
    person_id: int
    can_attend: bool
    available_minutes: int

    class Config:
        from_attributes = True