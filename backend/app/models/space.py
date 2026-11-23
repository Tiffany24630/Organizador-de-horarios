from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from app.database.base import Base

class Space(Base):
    __tablename__ = "spaces"

    id_space: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id_project", ondelete="CASCADE"), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    capacity: Mapped[int] = mapped_column(Integer)
    reservations = relationship("SpaceReservation", back_populates="space", cascade="all, delete")
    project = relationship("Project")
