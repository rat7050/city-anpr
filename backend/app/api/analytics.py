from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

from backend.app.database import get_db
from backend.app.schemas.analytics import (
    TrafficStatsResponse, VehicleCountByCamera, VehicleCountByHour, 
    VehicleCountByZone, CongestionData, HeatmapResponse, ODMatrixResponse
)
from backend.app.services.analytics_service import (
    get_traffic_stats, get_vehicle_count_by_camera, get_vehicle_count_by_hour,
    get_vehicle_count_by_zone, get_congestion_data, get_heatmap_data, get_od_matrix
)
from backend.app.middleware.auth_middleware import get_current_user
from backend.app.models import User

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

@router.get("/stats", response_model=TrafficStatsResponse)
async def stats(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await get_traffic_stats(db)

@router.get("/vehicles-by-camera", response_model=List[VehicleCountByCamera])
async def vehicles_by_camera(
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await get_vehicle_count_by_camera(db, start_time, end_time)

@router.get("/vehicles-by-hour", response_model=List[VehicleCountByHour])
async def vehicles_by_hour(
    date: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await get_vehicle_count_by_hour(db, date)

@router.get("/vehicles-by-zone", response_model=List[VehicleCountByZone])
async def vehicles_by_zone(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await get_vehicle_count_by_zone(db)

@router.get("/congestion", response_model=List[CongestionData])
async def congestion(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await get_congestion_data(db)

@router.get("/heatmap", response_model=HeatmapResponse)
async def heatmap(
    metric: str = Query("density"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await get_heatmap_data(db, metric)

@router.get("/od-matrix", response_model=ODMatrixResponse)
async def od_matrix(
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await get_od_matrix(db, start_time, end_time)
