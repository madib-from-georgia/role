"""
Pydantic схемы для JWT токенов.
"""

from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class TokenBase(BaseModel):
    """Базовая схема токена."""
    token_type: str = Field(default="access", pattern="^(access|refresh)$")
    expires_at: datetime


class TokenCreate(TokenBase):
    """Схема для создания токена."""
    user_id: int
    token_hash: str = Field(..., min_length=1, max_length=255)


class TokenUpdate(BaseModel):
    """Схема для обновления токена."""
    is_revoked: Optional[bool] = None


class TokenInDBBase(TokenBase):
    """Базовая схема токена в БД."""
    id: int
    user_id: int
    token_hash: str
    is_revoked: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(TokenInDBBase):
    """Схема токена для API."""
    pass


class TokenData(BaseModel):
    """Данные токена для декодирования."""
    user_id: Optional[int] = None
    username: Optional[str] = None


class TokenResponse(BaseModel):
    """Ответ с токенами."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # секунды до истечения access token
