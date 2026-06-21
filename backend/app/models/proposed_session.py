from datetime import time
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Time
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from app.database.base import Base
from app.models.enums import DayOfWeek

class ProposedSession(Base):
    __tablename__ = "proposed_sessions"

    id_session: Mapped[int] = mapped_column(Integer, primary_key=True)
    schedule_id: Mapped[int] = mapped_column(ForeignKey("proposed_schedules.id_schedule", ondelete="CASCADE"))
    day_of_week: Mapped[DayOfWeek] = mapped_column(Enum(DayOfWeek))
    start_time: Mapped[time] = mapped_column(Time)
    end_time: Mapped[time] = mapped_column(Time)

    schedule = relationship("ProposedSchedule", back_populates="sessions")