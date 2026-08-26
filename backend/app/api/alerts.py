from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from backend.app.database import get_db
from backend.app.schemas.alert import AlertResponse, AlertListResponse, AlertUpdate
from backend.app.services.alert_service import get_alerts, update_alert_status
from backend.app.middleware.auth_middleware import get_current_user, require_role
from backend.app.models import User

router = APIRouter(prefix="/api/alerts", tags=["alerts"])

@router.get("/", response_model=AlertListResponse)
async def list_alerts(
    alert_type: Optional[str] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    alerts, total = await get_alerts(db, alert_type, severity, status, skip, limit)
    return {"items": alerts, "total": total, "skip": skip, "limit": limit}

@router.put("/{alert_id}/status", response_model=AlertResponse)
async def edit_alert_status(
    alert_id: str,
    data: AlertUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "OPERATOR"))
):
    alert = await update_alert_status(db, alert_id, data.status)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert
