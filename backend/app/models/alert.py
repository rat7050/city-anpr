import uuid
from datetime import datetime
from sqlalchemy import String, Text, JSON, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from ..database import Base

class Alert(Base):
    __tablename__ = 'alerts'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('vehicles.id'), nullable=True)
    camera_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('cameras.id'), nullable=True)
    alert_type: Mapped[str] = mapped_column(String(50), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    status: Mapped[str] = mapped_column(String(20), default='ACTIVE')
    metadata_json: Mapped[dict] = mapped_column(JSON, nullable=True)

    vehicle = relationship("Vehicle", back_populates="alerts")
    camera = relationship("Camera", back_populates="alerts")
