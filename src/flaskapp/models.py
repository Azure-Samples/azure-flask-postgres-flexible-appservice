from typing import List, Optional

from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import db

association_table = db.Table(
    "cruise_destination_link",
    Column("cruise_id", ForeignKey("cruise.id"), primary_key=True),
    Column("destination_id", ForeignKey("destination.id"), primary_key=True),
)


class Destination(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    subtitle: Mapped[Optional[str]] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(String(1000))
    cruises: Mapped[List["Cruise"]] = relationship("Cruise", secondary=association_table, back_populates="destinations")

    def __str__(self):
        return self.name


class Cruise(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    subtitle: Mapped[Optional[str]] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(String(1000))
    destinations: Mapped[List[Destination]] = relationship(
        "Destination", secondary=association_table, back_populates="cruises"
    )

    def __str__(self):
        return self.name


class InfoRequest(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255))
    notes: Mapped[str] = mapped_column(String(255))
    cruise_id: Mapped[int] = mapped_column(ForeignKey("cruise.id"))
