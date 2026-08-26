from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class VehicleResponse(BaseModel):
    id: UUID
    plate_number: str
    vehicle_type: Optional[str]
    vehicle_color: Optional[str]
    first_seen: Optional[datetime]
    last_seen: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)

class VehicleSearchResponse(BaseModel):
    vehicle: VehicleResponse
    detection_count: int
    camera_count: int

class VehicleListResponse(BaseModel):
    vehicles: List[VehicleResponse]
    total: int
