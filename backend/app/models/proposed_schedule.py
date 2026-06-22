from sqlalchemy import Integer
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import String
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

    attendance_percentage: Mapped[float]
    attendances = relationship("ProposalAttendance", cascade="all, delete-orphan")
    score: Mapped[float]

    status: Mapped[ProposalStatus] = mapped_column(Enum(ProposalStatus), default=ProposalStatus.PENDING)

    group = relationship("ActivityGroup")
    sessions = relationship("ProposedSession", cascade="all, delete-orphan", back_populates="schedule")