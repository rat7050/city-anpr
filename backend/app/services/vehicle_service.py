from typing import Tuple, List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from backend.app.models import Vehicle

async def search_vehicles(
    db: AsyncSession, plate_query: Optional[str] = None, vehicle_type: Optional[str] = None, skip: int = 0, limit: int = 100
) -> Tuple[List[Vehicle], int]:
    stmt = select(Vehicle)
    if plate_query:
        stmt = stmt.where(Vehicle.plate_number.ilike(f"%{plate_query}%"))
    if vehicle_type:
        stmt = stmt.where(Vehicle.vehicle_type == vehicle_type)
        
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = await db.scalar(count_stmt)
    
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    vehicles = list(result.scalars().all())
    
    return vehicles, total or 0

async def get_vehicle_by_plate(db: AsyncSession, plate_number: str) -> Optional[Vehicle]:
    stmt = select(Vehicle).where(Vehicle.plate_number == plate_number)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def get_or_create_vehicle(
    db: AsyncSession, plate_number: str, vehicle_type: Optional[str] = None, vehicle_color: Optional[str] = None
) -> Vehicle:
    vehicle = await get_vehicle_by_plate(db, plate_number)
    if not vehicle:
        vehicle = Vehicle(
            plate_number=plate_number,
            vehicle_type=vehicle_type,
            vehicle_color=vehicle_color
        )
        db.add(vehicle)
        await db.commit()
        await db.refresh(vehicle)
    return vehicle

async def update_vehicle_last_seen(db: AsyncSession, vehicle_id: str, timestamp: datetime) -> None:
    stmt = select(Vehicle).where(Vehicle.id == vehicle_id)
    result = await db.execute(stmt)
    vehicle = result.scalar_one_or_none()
    if vehicle:
        vehicle.last_seen = timestamp
        if not vehicle.first_seen:
            vehicle.first_seen = timestamp
        await db.commit()
