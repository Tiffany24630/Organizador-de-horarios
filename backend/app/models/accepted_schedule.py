from sqlalchemy import Integer
from sqlalchemy import ForeignKey
from sqlalchemy import DateTime
from datetime import datetime
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from app.database.base import Base

class AcceptedSchedule(Base):
    __tablename__ = "accepted_schedules"

    id_accepted: Mapped[int] = mapped_column(Integer, primary_key=True)
    proposal_id: Mapped[int] = mapped_column(ForeignKey("proposed_schedules.id_schedule"))
    accepted_at: Mapped[datetime] = mapped_column(DateTime)

    proposal = relationship("ProposedSchedule")