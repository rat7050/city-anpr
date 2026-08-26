from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

class AlertCreate(BaseModel):
    vehicle_id: Optional[UUID] = None
    camera_id: Optional[UUID] = None
    alert_type: str
    severity: str
    message: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None

class AlertResponse(BaseModel):
    id: UUID
    vehicle_id: Optional[UUID]
    camera_id: Optional[UUID]
    plate_number: Optional[str] = None
    camera_name: Optional[str] = None
    alert_type: str
    severity: str
    message: Optional[str]
    timestamp: datetime
    status: str
    metadata_json: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)

class AlertListResponse(BaseModel):
    alerts: List[AlertResponse]
    total: int

class AlertUpdateRequest(BaseModel):
    status: str

AlertUpdate = AlertUpdateRequest
