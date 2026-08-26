from typing import Tuple, List, Optional
from datetime import datetime, timezone
import math
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from backend.app.models import Trajectory, Detection, Vehicle, Camera
from backend.app.schemas.trajectory import TrajectoryResponse, TrajectoryPoint

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
    
    if not detections:
        return None
        
    start_time = detections[0].timestamp
    end_time = detections[-1].timestamp
    
    total_distance = 0.0
    camera_ids = set()
    trajectory_points: List[TrajectoryPoint] = []
    
    # Load camera names lookup
    cam_stmt = select(Camera)
    cam_res = await db.execute(cam_stmt)
    cam_lookup = {c.id: c.camera_name for c in cam_res.scalars().all()}
    
    for i in range(len(detections)):
        det = detections[i]
        camera_ids.add(det.camera_id)
        cam_name = cam_lookup.get(det.camera_id, f"Cam-{str(det.camera_id)[:4]}")
        
        trajectory_points.append(TrajectoryPoint(
            camera_id=det.camera_id,
            camera_name=cam_name,
            latitude=det.latitude,
            longitude=det.longitude,
            timestamp=det.timestamp,
            ocr_confidence=det.ocr_confidence,
            direction=det.direction,
            speed=det.speed
        ))
        
        if i > 0:
            prev = detections[i-1]
            dist = haversine(prev.latitude, prev.longitude, det.latitude, det.longitude)
            total_distance += dist
            
    time_diff_hours = (end_time - start_time).total_seconds() / 3600.0 if end_time != start_time else 0.0
    average_speed = (total_distance / time_diff_hours) if time_diff_hours > 0 else 45.0
    total_distance = round(total_distance, 2)
    average_speed = round(average_speed, 1)
    
    # Create LineString WKT
    coords_wkt = [f"{p.longitude} {p.latitude}" for p in trajectory_points]
    line_wkt = f"LINESTRING({', '.join(coords_wkt)})"
    
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
    
    geojson = {
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": [[p.longitude, p.latitude] for p in trajectory_points]
        },
        "properties": {
            "plate_number": plate_number,
            "distance": total_distance,
            "speed": average_speed
        }
    }
    
    return TrajectoryResponse(
        id=trajectory.id,
        vehicle_id=vehicle.id,
        plate_number=plate_number,
        start_time=start_time,
        end_time=end_time,
        distance=total_distance,
        average_speed=average_speed,
        camera_count=len(camera_ids),
        points=trajectory_points,
        route_geojson=geojson
    )

async def get_vehicle_trajectory(db: AsyncSession, plate_number: str) -> Optional[TrajectoryResponse]:
    return await build_trajectory(db, plate_number)
