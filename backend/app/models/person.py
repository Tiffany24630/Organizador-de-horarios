from sqlalchemy import Boolean
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from app.database.base import Base

class Person(Base):
    __tablename__ = "persons"

    id_person: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id_project", ondelete="CASCADE"), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    activities = relationship("Activity", back_populates="person", cascade="all, delete")
    participants = relationship("GroupParticipant", back_populates="person", cascade="all, delete-orphan")
    proposal_attendances = relationship("ProposalAttendance", back_populates="person")
    project = relationship("Project")
