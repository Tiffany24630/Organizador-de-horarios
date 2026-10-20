from pydantic import BaseModel, Field

class ProposalAttendanceResponse(BaseModel):
    id_attendance: int
    proposal_id: int
    person_id: int
    can_attend: bool
    available_minutes: int
    reason: str | None = None
    conflicts: list[dict] = Field(default_factory=list)

    class Config:
        from_attributes = True
