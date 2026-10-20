from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy import Time
from datetime import time
from sqlalchemy import Enum
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from app.database.base import Base
from app.models.enums import DayOfWeek

class TimeBlock(Base):
    __tablename__ = "time_blocks"

    id_block: Mapped[int] = mapped_column(Integer, primary_key=True)
    activity_id: Mapped[int] = mapped_column(ForeignKey("activities.id_activity", ondelete="CASCADE"))
    day_of_week: Mapped[DayOfWeek] = mapped_column(Enum(DayOfWeek))
    start_time: Mapped[time] = mapped_column(Time)
    end_time: Mapped[time] = mapped_column(Time)
    # Optional so existing schedules and imports without a classroom remain valid.
    room: Mapped[str | None] = mapped_column(String(100), nullable=True)
    activity = relationship("Activity", back_populates="time_blocks")
