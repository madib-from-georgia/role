"""
Dependencies для авторизации.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database.connection import get_db_session
from app.database.models.user import User
from app.services.auth import auth_service


# HTTP Bearer схема для токенов
security = HTTPBearer(auto_error=False)


def get_db():
    """Dependency для получения сессии БД."""
    with get_db_session() as db:
        yield db


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency для получения текущего авторизованного пользователя.
    
    Raises:
        HTTPException: 401 если токен невалиден
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неверные учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not credentials:
        raise credentials_exception
    
    token = credentials.credentials
    user = auth_service.get_current_user(db, token)
    
    if user is None:
        raise credentials_exception
    
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency для получения текущего активного пользователя.
    
    Raises:
        HTTPException: 400 если пользователь неактивен
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Неактивный пользователь"
        )
    return current_user


def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Dependency для получения текущего пользователя (опционально).
    
    Возвращает None если авторизация не предоставлена или невалидна.
    """
    if not credentials:
        return None
    
    token = credentials.credentials
    user = auth_service.get_current_user(db, token)
    
    return user if user and user.is_active else None
