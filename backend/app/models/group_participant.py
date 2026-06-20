from sqlalchemy import Boolean
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from app.database.base import Base

class GroupParticipant(Base):
    __tablename__ = "group_participants"

    id_participant: Mapped[int] = mapped_column(Integer, primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("activity_groups.id_group", ondelete="CASCADE"))
    person_id: Mapped[int] = mapped_column(ForeignKey("persons.id_person", ondelete="CASCADE"))
    required: Mapped[bool] = mapped_column(Boolean, default=True)
    group = relationship("ActivityGroup", back_populates="participants")
    person = relationship("Person")