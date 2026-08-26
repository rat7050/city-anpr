from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class WatchlistCreate(BaseModel):
    plate_number: str
    reason: Optional[str] = None
    priority: Optional[str] = "MEDIUM"

class WatchlistResponse(BaseModel):
    id: UUID
    plate_number: str
    reason: Optional[str]
    status: str
    priority: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class WatchlistListResponse(BaseModel):
    entries: List[WatchlistResponse]
    total: int
