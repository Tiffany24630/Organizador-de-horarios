from sqlalchemy import Boolean
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from app.database.base import Base
from sqlalchemy import Integer

class ProposalAttendance(Base):
    __tablename__ = "proposal_attendance"

    id_attendance: Mapped[int] = mapped_column(Integer, primary_key=True)
    proposal_id: Mapped[int] = mapped_column(ForeignKey("proposed_schedules.id_schedule", ondelete="CASCADE"))
    person_id: Mapped[int] = mapped_column(ForeignKey("persons.id_person", ondelete="CASCADE"))
    can_attend: Mapped[bool] = mapped_column(Boolean)

    available_minutes: Mapped[int] = mapped_column(Integer)

    proposal = relationship("ProposedSchedule")
    person = relationship("Person")