from typing import Tuple, List, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from backend.app.models import Detection, Camera
from backend.app.schemas.detection import DetectionCreate
from backend.app.services.vehicle_service import get_or_create_vehicle, update_vehicle_last_seen
from backend.app.services.alert_service import check_watchlist, create_alert
from backend.app.services.plate_validator import normalize_plate

async def create_detection(db: AsyncSession, data: DetectionCreate) -> Detection:
    normalized_plate = normalize_plate(data.plate_number)
    
    # 1. Get or create vehicle
    vehicle = await get_or_create_vehicle(db, normalized_plate, data.vehicle_type)
    
    # 2. Update vehicle last seen
    timestamp = data.timestamp or datetime.now(timezone.utc)
    await update_vehicle_last_seen(db, vehicle.id, timestamp)
    
    # 3. Create Detection
    point_wkt = f"POINT({data.longitude} {data.latitude})"
    detection = Detection(
        camera_id=data.camera_id,
        vehicle_id=vehicle.id,
        plate_number=normalized_plate,
        ocr_confidence=data.ocr_confidence,
        timestamp=timestamp,
        latitude=data.latitude,
        longitude=data.longitude,
        direction=data.direction,
        speed=data.speed,
        vehicle_type=data.vehicle_type,
        image_path=data.image_path,
        plate_image_path=data.plate_image_path,
        location=point_wkt
    )
    db.add(detection)
    
    # 4. Update camera detection count
    stmt = select(Camera).where(Camera.id == data.camera_id)
    camera = (await db.execute(stmt)).scalar_one_or_none()
    if camera:
        camera.detection_count += 1
        
    # 5. Check Watchlist
    watchlist_entry = await check_watchlist(db, normalized_plate)
    if watchlist_entry:
        await create_alert(
            db=db,
            vehicle_id=vehicle.id,
            camera_id=data.camera_id,
            alert_type="WATCHLIST_MATCH",
            severity=watchlist_entry.priority,
            message=f"Watchlist match for plate {normalized_plate}. Reason: {watchlist_entry.reason}",
            metadata_json={"watchlist_id": str(watchlist_entry.id), "confidence": data.ocr_confidence}
        )
        
    await db.commit()
    await db.refresh(detection)
    return detection

async def get_detections(
    db: AsyncSession, camera_id: Optional[str] = None, plate_number: Optional[str] = None, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None, skip: int = 0, limit: int = 100
) -> Tuple[List[Detection], int]:
    stmt = select(Detection)
    if camera_id:
        stmt = stmt.where(Detection.camera_id == camera_id)
    if plate_number:
        stmt = stmt.where(Detection.plate_number == plate_number)
    if start_time:
        stmt = stmt.where(Detection.timestamp >= start_time)
    if end_time:
        stmt = stmt.where(Detection.timestamp <= end_time)
        
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = await db.scalar(count_stmt)
    
    stmt = stmt.order_by(desc(Detection.timestamp)).offset(skip).limit(limit)
    result = await db.execute(stmt)
    detections = list(result.scalars().all())
    
    return detections, total or 0

async def get_vehicle_detections(db: AsyncSession, plate_number: str, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None) -> List[Detection]:
    stmt = select(Detection).where(Detection.plate_number == plate_number)
    if start_time:
        stmt = stmt.where(Detection.timestamp >= start_time)
    if end_time:
        stmt = stmt.where(Detection.timestamp <= end_time)
        
    stmt = stmt.order_by(desc(Detection.timestamp))
    result = await db.execute(stmt)
    return list(result.scalars().all())

async def get_recent_detections(db: AsyncSession, limit: int = 20) -> List[Detection]:
    stmt = select(Detection).order_by(desc(Detection.timestamp)).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())
