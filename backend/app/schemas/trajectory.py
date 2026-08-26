from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Any, Dict
from uuid import UUID
from datetime import datetime

class TrajectoryPoint(BaseModel):
    camera_id: UUID
    camera_name: str
    latitude: float
    longitude: float
    timestamp: datetime
    ocr_confidence: Optional[float] = None
    direction: Optional[str] = None
    speed: Optional[float] = None

class TrajectoryResponse(BaseModel):
    id: UUID
    vehicle_id: UUID
    plate_number: str
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    distance: Optional[float]
    average_speed: Optional[float]
    camera_count: Optional[int]
    points: List[TrajectoryPoint]
    route_geojson: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)
