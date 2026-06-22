from datetime import time
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Time
from sqlalchemy.orm import Mapped
from sqlalchemy import Enum
from app.models.enums import RestrictionType
from app.models.enums import DayOfWeek
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from app.database.base import Base

class Restriction(Base):
    __tablename__ = "restrictions"

    id_restriction: Mapped[int] = mapped_column(Integer, primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("activity_groups.id_group", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    start_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    end_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    type: Mapped[RestrictionType] = mapped_column(Enum(RestrictionType))
    day_of_week: Mapped[DayOfWeek | None] = mapped_column(Enum(DayOfWeek), nullable=True)

    group = relationship("ActivityGroup", back_populates="restrictions")