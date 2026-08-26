from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from backend.app.database import get_db
from backend.app.schemas.watchlist import WatchlistResponse, WatchlistCreate, WatchlistListResponse
from backend.app.services.watchlist_service import get_watchlist, add_to_watchlist, remove_from_watchlist, update_watchlist_entry
from backend.app.middleware.auth_middleware import get_current_user, require_role
from backend.app.models import User

router = APIRouter(prefix="/api/watchlist", tags=["watchlist"])

@router.get("/", response_model=WatchlistListResponse)
async def list_watchlist(
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    items, total = await get_watchlist(db, status, skip, limit)
    return {"items": items, "total": total, "skip": skip, "limit": limit}

@router.post("/", response_model=WatchlistResponse)
async def create_watchlist_entry(
    data: WatchlistCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "OPERATOR"))
):
    return await add_to_watchlist(db, data, current_user.id)

@router.delete("/{watchlist_id}")
async def delete_watchlist_entry(
    watchlist_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "OPERATOR"))
):
    success = await remove_from_watchlist(db, watchlist_id)
    if not success:
        raise HTTPException(status_code=404, detail="Watchlist entry not found")
    return {"message": "Watchlist entry removed successfully"}
