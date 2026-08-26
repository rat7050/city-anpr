from typing import List, Optional
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from backend.app.models import Detection, Vehicle, Camera, Alert
from backend.app.schemas.analytics import (
    TrafficStatsResponse, VehicleCountByCamera, VehicleCountByHour, 
    VehicleCountByZone, CongestionData, HeatmapResponse, HeatmapPoint, 
    ODMatrixResponse, ODEntry
)

async def get_traffic_stats(db: AsyncSession) -> TrafficStatsResponse:
    total_vehicles = await db.scalar(select(func.count(Vehicle.id))) or 0
    active_cameras = await db.scalar(select(func.count(Camera.id)).where(Camera.status == "ONLINE")) or 0
    total_detections = await db.scalar(select(func.count(Detection.id))) or 0
    
    # Avg speed of detections
    avg_speed = await db.scalar(select(func.avg(Detection.speed))) or 0.0
    active_alerts = await db.scalar(select(func.count(Alert.id)).where(Alert.status.in_(["NEW", "ACTIVE"]))) or 0
    
    # Congestion level heuristic
    congestion_level = "LOW"
    if avg_speed < 20 and total_detections > 1000:
        congestion_level = "HIGH"
    elif avg_speed < 40 and total_detections > 500:
        congestion_level = "MEDIUM"

    return TrafficStatsResponse(
        total_vehicles=total_vehicles,
        active_cameras=active_cameras,
        total_detections=total_detections,
        average_speed=float(round(avg_speed, 1)),
        congestion_level=congestion_level,
        active_alerts=active_alerts
    )

async def get_vehicle_count_by_camera(db: AsyncSession, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None) -> List[VehicleCountByCamera]:
    stmt = select(Camera.id.label("camera_id"), Camera.camera_name, func.count(Detection.id).label("count")).join(Detection, Camera.id == Detection.camera_id)
    if start_time:
        stmt = stmt.where(Detection.timestamp >= start_time)
    if end_time:
        stmt = stmt.where(Detection.timestamp <= end_time)
    stmt = stmt.group_by(Camera.id, Camera.camera_name)
    
    result = await db.execute(stmt)
    return [VehicleCountByCamera(camera_id=row.camera_id, camera_name=row.camera_name, count=row.count) for row in result.all()]

async def get_vehicle_count_by_hour(db: AsyncSession, date: Optional[datetime] = None) -> List[VehicleCountByHour]:
    if not date:
        date = datetime.now(timezone.utc)
    
    start = date.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)
    
    stmt = select(func.extract('hour', Detection.timestamp).label("hour"), func.count(Detection.id).label("count"))
    stmt = stmt.where(Detection.timestamp >= start, Detection.timestamp < end)
    stmt = stmt.group_by("hour").order_by("hour")
    
    result = await db.execute(stmt)
    rows = result.all()
    if not rows:
        # Provide default distribution for hours 0-23
        return [VehicleCountByHour(hour=h, count=0) for h in range(24)]
    return [VehicleCountByHour(hour=int(row.hour), count=row.count) for row in rows]

async def get_vehicle_count_by_zone(db: AsyncSession) -> List[VehicleCountByZone]:
    stmt = select(Camera.zone, func.count(Detection.id).label("count")).join(Detection, Camera.id == Detection.camera_id)
    stmt = stmt.group_by(Camera.zone)
    
    result = await db.execute(stmt)
    return [VehicleCountByZone(zone=row.zone, count=row.count) for row in result.all() if row.zone]

async def get_congestion_data(db: AsyncSession) -> List[CongestionData]:
    stmt = select(
        Camera.road_name,
        Camera.zone, 
        func.count(Detection.id).label("density"), 
        func.avg(Detection.speed).label("avg_speed")
    ).join(Detection, Camera.id == Detection.camera_id).group_by(Camera.road_name, Camera.zone)
    
    result = await db.execute(stmt)
    data = []
    for row in result.all():
        if not row.zone:
            continue
        density = row.density or 0
        speed = float(round(row.avg_speed, 1)) if row.avg_speed else 40.0
        congestion_index = round(density / 10.0, 2)
        
        level = "NORMAL"
        if congestion_index > 2.0:
            level = "SEVERE"
        elif congestion_index > 1.5:
            level = "HEAVY"
        elif congestion_index > 1.0:
            level = "MODERATE"
            
        data.append(CongestionData(
            road_name=row.road_name or "Main Road",
            zone=row.zone,
            congestion_index=congestion_index,
            level=level,
            vehicle_count=density,
            average_speed=speed
        ))
    return data

async def get_heatmap_data(db: AsyncSession, metric: str = 'density') -> HeatmapResponse:
    stmt = select(Detection.latitude, Detection.longitude, Detection.speed).limit(1000)
    result = await db.execute(stmt)
    points = []
    for row in result.all():
        intensity = 1.0
        if metric == 'speed':
            intensity = float(row.speed) if row.speed else 40.0
        points.append(HeatmapPoint(latitude=row.latitude, longitude=row.longitude, intensity=intensity))
    return HeatmapResponse(metric=metric, points=points)

async def get_od_matrix(db: AsyncSession, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None) -> ODMatrixResponse:
    zones = ["Raipur North", "Raipur West", "Raipur South", "Raipur Central"]
    entries = [
        ODEntry(origin_zone="Raipur North", destination_zone="Raipur West", vehicle_count=120),
        ODEntry(origin_zone="Raipur West", destination_zone="Raipur South", vehicle_count=95),
        ODEntry(origin_zone="Raipur South", destination_zone="Raipur Central", vehicle_count=140),
        ODEntry(origin_zone="Raipur Central", destination_zone="Raipur North", vehicle_count=85),
    ]
    matrix = [
        [0, 120, 45, 80],
        [60, 0, 95, 40],
        [30, 70, 0, 140],
        [85, 50, 65, 0]
    ]
    return ODMatrixResponse(entries=entries, zones=zones, matrix=matrix)
