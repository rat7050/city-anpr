from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID

class TrafficStatsResponse(BaseModel):
    total_vehicles: int
    active_cameras: int
    total_detections: int
    average_speed: Optional[float] = None
    congestion_level: str
    active_alerts: int

class VehicleCountByCamera(BaseModel):
    camera_id: Optional[UUID] = None
    camera_name: str
    count: int

class VehicleCountByHour(BaseModel):
    hour: int
    count: int

class VehicleCountByZone(BaseModel):
    zone: str
    count: int

class CongestionData(BaseModel):
    road_name: Optional[str] = None
    zone: Optional[str] = None
    congestion_index: float
    level: str
    vehicle_count: int
    average_speed: Optional[float] = None

class ODEntry(BaseModel):
    origin_zone: str
    destination_zone: str
    vehicle_count: int

ODMatrixEntry = ODEntry

class ODMatrixResponse(BaseModel):
    entries: List[ODEntry]
    zones: List[str]
    matrix: List[List[int]]

class HeatmapPoint(BaseModel):
    latitude: float
    longitude: float
    intensity: float

class HeatmapResponse(BaseModel):
    points: List[HeatmapPoint]
    metric: str
