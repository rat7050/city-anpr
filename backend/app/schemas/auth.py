from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    role: str
    username: str

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str = "VIEWER"

class UserResponse(BaseModel):
    id: UUID
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
