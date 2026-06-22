from sqlalchemy import Boolean
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from app.database.base import Base

class Person(Base):
    __tablename__ = "persons"

    id_person: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    activities = relationship("Activity", back_populates="person", cascade="all, delete")