from typing import Tuple, List, Optional
from datetime import datetime, timezone
import math
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from backend.app.models import Trajectory, Detection, Vehicle
from backend.app.schemas.trajectory import TrajectoryResponse

def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great circle distance in kilometers between two points on the earth."""
    R = 6371.0 # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

async def build_trajectory(db: AsyncSession, plate_number: str) -> Optional[TrajectoryResponse]:
    # Find vehicle
    stmt = select(Vehicle).where(Vehicle.plate_number == plate_number)
    result = await db.execute(stmt)
    vehicle = result.scalar_one_or_none()
    
    if not vehicle:
        return None
        
    # Get all detections sorted by timestamp
    stmt = select(Detection).where(Detection.vehicle_id == vehicle.id).order_by(Detection.timestamp)
    result = await db.execute(stmt)
    detections = list(result.scalars().all())
    
    if not detections or len(detections) < 2:
        return None
        
    start_time = detections[0].timestamp
    end_time = detections[-1].timestamp
    
    total_distance = 0.0
    camera_ids = set()
    points = []
    
    for i in range(len(detections)):
        det = detections[i]
        camera_ids.add(det.camera_id)
        points.append(f"{det.longitude} {det.latitude}")
        
        if i > 0:
            prev = detections[i-1]
            dist = haversine(prev.latitude, prev.longitude, det.latitude, det.longitude)
            total_distance += dist
            
    time_diff_hours = (end_time - start_time).total_seconds() / 3600.0
    average_speed = (total_distance / time_diff_hours) if time_diff_hours > 0 else 0.0
    
    # Create LineString WKT
    line_wkt = f"LINESTRING({', '.join(points)})"
    
    # Check if trajectory exists
    stmt = select(Trajectory).where(Trajectory.vehicle_id == vehicle.id)
    result = await db.execute(stmt)
    trajectory = result.scalar_one_or_none()
    
    if not trajectory:
        trajectory = Trajectory(
            vehicle_id=vehicle.id,
            start_time=start_time,
            end_time=end_time,
            distance=total_distance,
            average_speed=average_speed,
            camera_count=len(camera_ids),
            route_geometry=line_wkt
        )
        db.add(trajectory)
    else:
        trajectory.start_time = start_time
        trajectory.end_time = end_time
        trajectory.distance = total_distance
        trajectory.average_speed = average_speed
        trajectory.camera_count = len(camera_ids)
        trajectory.route_geometry = line_wkt
        
    await db.commit()
    await db.refresh(trajectory)
    
    # Normally we would convert WKT/PostGIS to GeoJSON. Here we mock or map.
    # We will let the schema handle it if defined, or return it directly.
    return TrajectoryResponse.model_validate(trajectory)

async def get_vehicle_trajectory(db: AsyncSession, plate_number: str) -> Optional[TrajectoryResponse]:
    # We rebuild to ensure latest data is included, or we can just fetch if we assume it's updated synchronously.
    # For now, let's just build it.
    return await build_trajectory(db, plate_number)
