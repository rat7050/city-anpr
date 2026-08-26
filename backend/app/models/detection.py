import uuid
from datetime import datetime
from sqlalchemy import String, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .compat import UUIDType, GeometryText
from ..database import Base

class Detection(Base):
    __tablename__ = 'detections'

    id: Mapped[uuid.UUID] = mapped_column(UUIDType(), primary_key=True, default=uuid.uuid4)
    camera_id: Mapped[uuid.UUID] = mapped_column(UUIDType(), ForeignKey('cameras.id'), nullable=False)
    vehicle_id: Mapped[uuid.UUID] = mapped_column(UUIDType(), ForeignKey('vehicles.id'), nullable=True)
    plate_number: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    ocr_confidence: Mapped[float] = mapped_column(Float, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=True)
    direction: Mapped[str] = mapped_column(String(20), nullable=True)
    speed: Mapped[float] = mapped_column(Float, nullable=True)
    vehicle_type: Mapped[str] = mapped_column(String(50), nullable=True)
    image_path: Mapped[str] = mapped_column(String(500), nullable=True)
    plate_image_path: Mapped[str] = mapped_column(String(500), nullable=True)
    location: Mapped[str] = mapped_column(GeometryText(), nullable=True)

    camera = relationship("Camera", back_populates="detections")
    vehicle = relationship("Vehicle", back_populates="detections")
