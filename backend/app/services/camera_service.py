from typing import Tuple, List, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from backend.app.models import Camera
from backend.app.schemas.camera import CameraCreate, CameraUpdate

async def get_cameras(
    db: AsyncSession, skip: int = 0, limit: int = 100, zone: Optional[str] = None, status: Optional[str] = None
) -> Tuple[List[Camera], int]:
    stmt = select(Camera)
    if zone:
        stmt = stmt.where(Camera.zone == zone)
    if status:
        stmt = stmt.where(Camera.status == status)
    
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = await db.scalar(count_stmt)
    
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    cameras = list(result.scalars().all())
    
    return cameras, total or 0

async def get_camera(db: AsyncSession, camera_id: str) -> Optional[Camera]:
    stmt = select(Camera).where(Camera.id == camera_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def create_camera(db: AsyncSession, data: CameraCreate) -> Camera:
    # We will construct a PostGIS POINT for the location
    point_wkt = f"POINT({data.longitude} {data.latitude})"
    db_camera = Camera(
        camera_name=data.camera_name,
        latitude=data.latitude,
        longitude=data.longitude,
        road_name=data.road_name,
        zone=data.zone,
        status=data.status,
        stream_url=data.stream_url,
        location=point_wkt
    )
    db.add(db_camera)
    await db.commit()
    await db.refresh(db_camera)
    return db_camera

async def update_camera(db: AsyncSession, camera_id: str, data: CameraUpdate) -> Optional[Camera]:
    camera = await get_camera(db, camera_id)
    if not camera:
        return None
        
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(camera, key, value)
        
    if "latitude" in update_data or "longitude" in update_data:
        lat = update_data.get("latitude", camera.latitude)
        lon = update_data.get("longitude", camera.longitude)
        camera.location = f"POINT({lon} {lat})"
        
    await db.commit()
    await db.refresh(camera)
    return camera

async def delete_camera(db: AsyncSession, camera_id: str) -> bool:
    camera = await get_camera(db, camera_id)
    if not camera:
        return False
    await db.delete(camera)
    await db.commit()
    return True

async def update_camera_heartbeat(db: AsyncSession, camera_id: str) -> Optional[Camera]:
    camera = await get_camera(db, camera_id)
    if not camera:
        return None
    camera.last_heartbeat = datetime.now(timezone.utc)
    camera.status = "ONLINE"
    await db.commit()
    await db.refresh(camera)
    return camera

async def get_camera_stats(db: AsyncSession, camera_id: str) -> dict:
    camera = await get_camera(db, camera_id)
    if not camera:
        return {}
    # Fetch last detection time (placeholder for more complex queries)
    return {
        "detection_count": camera.detection_count,
        "last_heartbeat": camera.last_heartbeat,
        "status": camera.status
    }
