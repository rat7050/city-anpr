from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class DetectionCreate(BaseModel):
    camera_id: UUID
    plate_number: str
    ocr_confidence: Optional[float] = None
    timestamp: datetime
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    direction: Optional[str] = None
    speed: Optional[float] = None
    vehicle_type: Optional[str] = None
    image_path: Optional[str] = None
    plate_image_path: Optional[str] = None

class DetectionResponse(BaseModel):
    id: UUID
    camera_id: UUID
    camera_name: Optional[str] = None
    vehicle_id: Optional[UUID] = None
    plate_number: str
    ocr_confidence: Optional[float]
    timestamp: datetime
    latitude: Optional[float]
    longitude: Optional[float]
    direction: Optional[str]
    speed: Optional[float]
    vehicle_type: Optional[str]
    image_path: Optional[str]
    plate_image_path: Optional[str]

    model_config = ConfigDict(from_attributes=True)

class DetectionListResponse(BaseModel):
    detections: List[DetectionResponse]
    total: int
