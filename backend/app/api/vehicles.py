from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from backend.app.database import get_db
from backend.app.schemas.vehicle import VehicleResponse, VehicleListResponse
from backend.app.schemas.trajectory import TrajectoryResponse
from backend.app.schemas.detection import DetectionResponse
from backend.app.services.vehicle_service import search_vehicles, get_vehicle_by_plate
from backend.app.services.trajectory_service import get_vehicle_trajectory
from backend.app.services.detection_service import get_vehicle_detections
from backend.app.middleware.auth_middleware import get_current_user
from backend.app.models import User

router = APIRouter(prefix="/api/vehicles", tags=["vehicles"])

@router.get("/", response_model=VehicleListResponse)
async def list_vehicles(
    plate: Optional[str] = None,
    vehicle_type: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    vehicles, total = await search_vehicles(db, plate, vehicle_type, skip, limit)
    return {"vehicles": vehicles, "total": total}

@router.get("/{plate_number}", response_model=VehicleResponse)
async def read_vehicle(plate_number: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    vehicle = await get_vehicle_by_plate(db, plate_number)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle

@router.get("/{plate_number}/trajectory", response_model=TrajectoryResponse)
async def read_vehicle_trajectory(plate_number: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    trajectory = await get_vehicle_trajectory(db, plate_number)
    if not trajectory:
        raise HTTPException(status_code=404, detail="Trajectory not found or not enough data")
    return trajectory

@router.get("/{plate_number}/detections", response_model=List[DetectionResponse])
async def read_vehicle_detections(
    plate_number: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    detections = await get_vehicle_detections(db, plate_number)
    return detections
