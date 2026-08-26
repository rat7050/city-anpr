import uuid
from datetime import datetime
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .compat import UUIDType
from ..database import Base

class Vehicle(Base):
    __tablename__ = 'vehicles'

    id: Mapped[uuid.UUID] = mapped_column(UUIDType(), primary_key=True, default=uuid.uuid4)
    plate_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    vehicle_type: Mapped[str] = mapped_column(String(50), nullable=True)
    vehicle_color: Mapped[str] = mapped_column(String(50), nullable=True)
    first_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    detections = relationship("Detection", back_populates="vehicle")
    trajectories = relationship("Trajectory", back_populates="vehicle")
    alerts = relationship("Alert", back_populates="vehicle")
