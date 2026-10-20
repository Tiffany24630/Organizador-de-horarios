from sqlalchemy import Integer
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import Enum
from app.models.enums import ProposalStatus
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from app.database.base import Base

class ProposedSchedule(Base):
    __tablename__ = "proposed_schedules"

    id_schedule: Mapped[int] = mapped_column(Integer, primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("activity_groups.id_group", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(100))

    attendances = relationship("ProposalAttendance", back_populates="proposal", cascade="all, delete-orphan")
    
    attendance_percentage: Mapped[float] = mapped_column(Float)
    score: Mapped[float] = mapped_column(Float)
    attending_count: Mapped[int] = mapped_column(Integer, default=0)
    total_people: Mapped[int] = mapped_column(Integer, default=0)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[ProposalStatus] = mapped_column(Enum(ProposalStatus), default=ProposalStatus.PENDING)

    group = relationship("ActivityGroup", back_populates="schedules")
    sessions = relationship("ProposedSession", cascade="all, delete-orphan", back_populates="schedule")
    accepted_schedule = relationship("AcceptedSchedule", uselist=False, back_populates="proposal")
