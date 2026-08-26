from typing import Tuple, List, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from backend.app.models import Alert, Watchlist
from backend.app.schemas.alert import AlertCreate

async def create_alert(
    db: AsyncSession, vehicle_id: str, camera_id: str, alert_type: str, severity: str, message: str, metadata_json: dict = None
) -> Alert:
    alert = Alert(
        vehicle_id=vehicle_id,
        camera_id=camera_id,
        alert_type=alert_type,
        severity=severity,
        message=message,
        metadata_json=metadata_json,
        timestamp=datetime.now(timezone.utc),
        status="NEW"
    )
    db.add(alert)
    await db.commit()
    await db.refresh(alert)
    return alert

async def get_alerts(
    db: AsyncSession, alert_type: Optional[str] = None, severity: Optional[str] = None, status: Optional[str] = None, skip: int = 0, limit: int = 100
) -> Tuple[List[Alert], int]:
    stmt = select(Alert)
    if alert_type:
        stmt = stmt.where(Alert.alert_type == alert_type)
    if severity:
        stmt = stmt.where(Alert.severity == severity)
    if status:
        stmt = stmt.where(Alert.status == status)
        
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = await db.scalar(count_stmt)
    
    stmt = stmt.order_by(Alert.timestamp.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    alerts = list(result.scalars().all())
    
    return alerts, total or 0

async def update_alert_status(db: AsyncSession, alert_id: str, status: str) -> Optional[Alert]:
    stmt = select(Alert).where(Alert.id == alert_id)
    result = await db.execute(stmt)
    alert = result.scalar_one_or_none()
    if alert:
        alert.status = status
        await db.commit()
        await db.refresh(alert)
    return alert

async def check_watchlist(db: AsyncSession, plate_number: str) -> Optional[Watchlist]:
    stmt = select(Watchlist).where(Watchlist.plate_number == plate_number, Watchlist.status == "ACTIVE")
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def get_active_alerts_count(db: AsyncSession) -> int:
    stmt = select(func.count(Alert.id)).where(Alert.status == "NEW")
    result = await db.scalar(stmt)
    return result or 0
