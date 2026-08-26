from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class CameraCreate(BaseModel):
    camera_name: str
    latitude: float
    longitude: float
    road_name: Optional[str] = None
    zone: Optional[str] = None
    stream_url: Optional[str] = None

class CameraUpdate(BaseModel):
    camera_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    road_name: Optional[str] = None
    zone: Optional[str] = None
    status: Optional[str] = None
    stream_url: Optional[str] = None

class CameraResponse(BaseModel):
    id: UUID
    camera_name: str
    latitude: float
    longitude: float
    road_name: Optional[str]
    zone: Optional[str]
    status: str
    stream_url: Optional[str]
    last_heartbeat: Optional[datetime]
    detection_count: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CameraListResponse(BaseModel):
    cameras: List[CameraResponse]
    total: int
