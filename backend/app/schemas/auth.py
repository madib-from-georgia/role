"""
Pydantic схемы для авторизации.
"""

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
    full_name: str = Field(None, max_length=255)


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
    full_name: str = None
    is_active: bool
    created_at: str
    
    model_config = {"from_attributes": True}