"""
Pydantic схемы для авторизации.
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Схема для входа в систему."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)


class RegisterRequest(BaseModel):
    """Схема для регистрации пользователя."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=8, max_length=100)
    full_name: Optional[str] = Field(None, max_length=255)


class RefreshTokenRequest(BaseModel):
    """Схема для обновления токена."""
    refresh_token: str


class LogoutRequest(BaseModel):
    """Схема для выхода из системы."""
    access_token: str


class AuthResponse(BaseModel):
    """Базовая схема ответа авторизации."""
    message: str
    success: bool = True


class UserProfileResponse(BaseModel):
    """Схема ответа с профилем пользователя."""
    id: int
    email: str
    username: str
    full_name: Optional[str] = None
    is_active: bool
    created_at: str
    
    model_config = {"from_attributes": True}


class ChangePasswordRequest(BaseModel):
    """Схема для смены пароля."""
    current_password: str = Field(..., min_length=8, max_length=100)
    new_password: str = Field(..., min_length=8, max_length=100)


class UpdateProfileRequest(BaseModel):
    """Схема для обновления профиля."""
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    full_name: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None
