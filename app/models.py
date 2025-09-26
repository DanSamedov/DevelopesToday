from typing import List, Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Boolean, Text, ForeignKey
from .db import Base


class Cat(Base):
    __tablename__ = "cats"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    years_experience: Mapped[int] = mapped_column(Integer)
    breed: Mapped[str] = mapped_column(String(100))
    salary: Mapped[int] = mapped_column(Integer)
    missions: Mapped[List["Mission"]] = relationship(back_populates="cat")


class Mission(Base):
    __tablename__ = "missions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    cat_id: Mapped[Optional[int]] = mapped_column(ForeignKey("cats.id"), nullable=True)
    cat = relationship("Cat", back_populates="missions")
    targets: Mapped[List["Target"]] = relationship(
        back_populates="mission", cascade="all, delete-orphan"
    )


class Target(Base):
    __tablename__ = "targets"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    country: Mapped[str] = mapped_column(String(80))
    notes: Mapped[str] = mapped_column(Text, default="")
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    mission_id: Mapped[int] = mapped_column(ForeignKey("missions.id"))
    mission = relationship("Mission", back_populates="targets")
