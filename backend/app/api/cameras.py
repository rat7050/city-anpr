from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from backend.app.database import get_db
from backend.app.schemas.camera import CameraResponse, CameraCreate, CameraUpdate, CameraListResponse
from backend.app.services.camera_service import get_cameras, get_camera, create_camera, update_camera, delete_camera, update_camera_heartbeat, get_camera_stats
from backend.app.middleware.auth_middleware import get_current_user, require_role
from backend.app.models import User

router = APIRouter(prefix="/api/cameras", tags=["cameras"])

@router.get("/", response_model=CameraListResponse)
async def list_cameras(
    zone: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cameras, total = await get_cameras(db, skip, limit, zone, status)
    return {"items": cameras, "total": total, "skip": skip, "limit": limit}

@router.get("/{camera_id}", response_model=CameraResponse)
async def read_camera(camera_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    camera = await get_camera(db, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    stats = await get_camera_stats(db, camera_id)
    return camera

@router.post("/", response_model=CameraResponse)
async def add_camera(
    data: CameraCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "OPERATOR"))
):
    return await create_camera(db, data)

@router.put("/{camera_id}", response_model=CameraResponse)
async def edit_camera(
    camera_id: str,
    data: CameraUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "OPERATOR"))
):
    camera = await update_camera(db, camera_id, data)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    return camera

@router.delete("/{camera_id}")
async def remove_camera(
    camera_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN"))
):
    success = await delete_camera(db, camera_id)
    if not success:
        raise HTTPException(status_code=404, detail="Camera not found")
    return {"message": "Camera deleted successfully"}

@router.post("/{camera_id}/heartbeat", response_model=CameraResponse)
async def heartbeat(
    camera_id: str,
    db: AsyncSession = Depends(get_db)
    # Auth might be different for cameras (e.g. API key) but keeping it simple for now
):
    camera = await update_camera_heartbeat(db, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    return camera
