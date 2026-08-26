from typing import List, Optional
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from backend.app.models import Detection, Vehicle, Camera, Alert
from backend.app.schemas.analytics import TrafficStatsResponse, VehicleCountByCamera, VehicleCountByHour, VehicleCountByZone, CongestionData, HeatmapResponse, HeatmapPoint, ODMatrixResponse, ODMatrixEntry

async def get_traffic_stats(db: AsyncSession) -> TrafficStatsResponse:
    total_vehicles = await db.scalar(select(func.count(Vehicle.id))) or 0
    active_cameras = await db.scalar(select(func.count(Camera.id)).where(Camera.status == "ONLINE")) or 0
    total_detections = await db.scalar(select(func.count(Detection.id))) or 0
    
    # Avg speed of recent detections
    avg_speed = await db.scalar(select(func.avg(Detection.speed))) or 0.0
    active_alerts = await db.scalar(select(func.count(Alert.id)).where(Alert.status == "NEW")) or 0
    
    # Simple congestion level logic
    congestion_level = "LOW"
    if avg_speed < 20 and total_detections > 1000:
        congestion_level = "HIGH"
    elif avg_speed < 40 and total_detections > 500:
        congestion_level = "MEDIUM"

    return TrafficStatsResponse(
        total_unique_vehicles=total_vehicles,
        active_cameras=active_cameras,
        total_detections=total_detections,
        average_speed=float(avg_speed),
        congestion_level=congestion_level,
        active_alerts=active_alerts
    )

async def get_vehicle_count_by_camera(db: AsyncSession, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None) -> List[VehicleCountByCamera]:
    stmt = select(Camera.camera_name, func.count(Detection.id).label("count")).join(Detection, Camera.id == Detection.camera_id)
    if start_time:
        stmt = stmt.where(Detection.timestamp >= start_time)
    if end_time:
        stmt = stmt.where(Detection.timestamp <= end_time)
    stmt = stmt.group_by(Camera.camera_name)
    
    result = await db.execute(stmt)
    return [VehicleCountByCamera(camera_name=row.camera_name, count=row.count) for row in result.all()]

async def get_vehicle_count_by_hour(db: AsyncSession, date: Optional[datetime] = None) -> List[VehicleCountByHour]:
    if not date:
        date = datetime.now(timezone.utc)
    
    start = date.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)
    
    stmt = select(func.extract('hour', Detection.timestamp).label("hour"), func.count(Detection.id).label("count"))
    stmt = stmt.where(Detection.timestamp >= start, Detection.timestamp < end)
    stmt = stmt.group_by("hour").order_by("hour")
    
    result = await db.execute(stmt)
    return [VehicleCountByHour(hour=int(row.hour), count=row.count) for row in result.all()]

async def get_vehicle_count_by_zone(db: AsyncSession) -> List[VehicleCountByZone]:
    stmt = select(Camera.zone, func.count(Detection.id).label("count")).join(Detection, Camera.id == Detection.camera_id)
    stmt = stmt.group_by(Camera.zone)
    
    result = await db.execute(stmt)
    return [VehicleCountByZone(zone=row.zone, count=row.count) for row in result.all() if row.zone]

async def get_congestion_data(db: AsyncSession) -> List[CongestionData]:
    # Group detections by zone in the last 1 hour
    one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
    stmt = select(
        Camera.zone, 
        func.count(Detection.id).label("density"), 
        func.avg(Detection.speed).label("avg_speed")
    ).join(Detection, Camera.id == Detection.camera_id).where(Detection.timestamp >= one_hour_ago).group_by(Camera.zone)
    
    result = await db.execute(stmt)
    data = []
    for row in result.all():
        if not row.zone:
            continue
        # Prototype thresholds
        # normal: density < 100, heavy > 500
        density = row.density
        speed = float(row.avg_speed) if row.avg_speed else 0.0
        congestion_index = density / 100.0 if density else 0.0
        
        status = "NORMAL"
        if congestion_index > 2.0:
            status = "SEVERE"
        elif congestion_index > 1.5:
            status = "HEAVY"
        elif congestion_index > 1.0:
            status = "MODERATE"
            
        data.append(CongestionData(
            zone=row.zone,
            congestion_index=congestion_index,
            status=status,
            average_speed=speed,
            vehicle_density=density
        ))
    return data

async def get_heatmap_data(db: AsyncSession, metric: str = 'density') -> HeatmapResponse:
    # Just return all detections location with a weight
    stmt = select(Detection.latitude, Detection.longitude, Detection.speed).limit(1000)
    result = await db.execute(stmt)
    points = []
    for row in result.all():
        weight = 1.0
        if metric == 'speed':
            weight = float(row.speed) if row.speed else 0.0
        points.append(HeatmapPoint(latitude=row.latitude, longitude=row.longitude, weight=weight))
    return HeatmapResponse(metric=metric, points=points)

async def get_od_matrix(db: AsyncSession, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None) -> ODMatrixResponse:
    # Highly simplified OD Matrix: just a placeholder logic to represent the structure
    # In reality, it involves tracking individual vehicles across zones
    entries = []
    return ODMatrixResponse(entries=entries)
