from typing import Tuple, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timezone

from backend.app.models import Watchlist
from backend.app.schemas.watchlist import WatchlistCreate
from backend.app.services.plate_validator import normalize_plate

async def get_watchlist(db: AsyncSession, status: Optional[str] = None, skip: int = 0, limit: int = 100) -> Tuple[List[Watchlist], int]:
    stmt = select(Watchlist)
    if status:
        stmt = stmt.where(Watchlist.status == status)
        
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = await db.scalar(count_stmt)
    
    stmt = stmt.order_by(Watchlist.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    items = list(result.scalars().all())
    
    return items, total or 0

async def add_to_watchlist(db: AsyncSession, data: WatchlistCreate, user_id: Optional[str] = None) -> Watchlist:
    entry = Watchlist(
        plate_number=normalize_plate(data.plate_number),
        reason=data.reason,
        status="ACTIVE",
        priority=data.priority,
        created_by=user_id,
        created_at=datetime.now(timezone.utc)
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry

async def remove_from_watchlist(db: AsyncSession, watchlist_id: str) -> bool:
    stmt = select(Watchlist).where(Watchlist.id == watchlist_id)
    entry = (await db.execute(stmt)).scalar_one_or_none()
    if not entry:
        return False
    await db.delete(entry)
    await db.commit()
    return True

async def update_watchlist_entry(db: AsyncSession, watchlist_id: str, status: str) -> Optional[Watchlist]:
    stmt = select(Watchlist).where(Watchlist.id == watchlist_id)
    entry = (await db.execute(stmt)).scalar_one_or_none()
    if entry:
        entry.status = status
        await db.commit()
        await db.refresh(entry)
    return entry

async def is_on_watchlist(db: AsyncSession, plate_number: str) -> bool:
    stmt = select(Watchlist).where(Watchlist.plate_number == plate_number, Watchlist.status == "ACTIVE")
    result = await db.execute(stmt)
    return result.scalar_one_or_none() is not None
