from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

from backend.app.database import get_db
from backend.app.schemas.detection import DetectionResponse, DetectionCreate, DetectionListResponse
from backend.app.services.detection_service import create_detection, get_detections, get_recent_detections
from backend.app.middleware.auth_middleware import get_current_user
from backend.app.models import User

router = APIRouter(prefix="/api/detections", tags=["detections"])

@router.get("/", response_model=DetectionListResponse)
async def list_detections(
    camera_id: Optional[str] = None,
    plate_number: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    detections, total = await get_detections(db, camera_id, plate_number, start_time, end_time, skip, limit)
    return {"detections": detections, "total": total}

@router.post("/", response_model=DetectionResponse)
async def add_detection(
    data: DetectionCreate,
    db: AsyncSession = Depends(get_db)
    # Auth omitted for AI workers integration for simplicity, or use API key
):
    return await create_detection(db, data)

@router.get("/recent", response_model=List[DetectionResponse])
async def recent_detections(
    limit: int = Query(20, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await get_recent_detections(db, limit)
