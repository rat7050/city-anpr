import uuid
from datetime import datetime
from sqlalchemy import Float, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry
from ..database import Base

class Trajectory(Base):
    __tablename__ = 'trajectories'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('vehicles.id'), nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    distance: Mapped[float] = mapped_column(Float, nullable=True)
    average_speed: Mapped[float] = mapped_column(Float, nullable=True)
    camera_count: Mapped[int] = mapped_column(Integer, nullable=True)
    route_geometry: Mapped[str] = mapped_column(Geometry('LINESTRING', srid=4326), nullable=True)

    vehicle = relationship("Vehicle", back_populates="trajectories")
