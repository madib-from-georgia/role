"""
Pydantic схемы для пользователя.
"""

from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class UserBase(BaseModel):
    """Базовая схема пользователя."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: Optional[str] = Field(None, max_length=255)
    is_active: bool = True


class UserCreate(UserBase):
    """Схема для создания пользователя."""
    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseModel):
    """Схема для обновления пользователя."""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    full_name: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=8, max_length=100)


class UserInDBBase(UserBase):
    """Базовая схема пользователя в БД."""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class User(UserInDBBase):
    """Схема пользователя для API."""
    pass


class UserInDB(UserInDBBase):
    """Схема пользователя в БД с хешем пароля."""
    password_hash: str
