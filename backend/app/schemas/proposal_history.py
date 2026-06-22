from datetime import datetime
from pydantic import BaseModel

class ProposalHistoryResponse(BaseModel):
    id_history: int
    proposal_id: int
    action: str
    created_at: datetime

    class Config:
        from_attributes = True