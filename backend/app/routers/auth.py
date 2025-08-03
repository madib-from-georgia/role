"""
API endpoints для авторизации.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_db, get_current_active_user
from app.services.auth import auth_service
from app.schemas.auth import (
    LoginRequest, 
    RegisterRequest, 
    RefreshTokenRequest, 
    AuthResponse,
    UserProfileResponse
)
from app.schemas.token import TokenResponse
from app.schemas.user import UserCreate, User
from app.database.models.user import User as UserModel


router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Регистрация нового пользователя.
    
    - **email**: Email пользователя (уникальный)
    - **username**: Имя пользователя (уникальное)
    - **password**: Пароль (минимум 8 символов)
    - **full_name**: Полное имя (опционально)
    """
    try:
        user_data = UserCreate(
            email=request.email,
            username=request.username,
            password=request.password,
            full_name=request.full_name
        )
        
        created_user = auth_service.register_user(db, user_data)
        
        return AuthResponse(
            message=f"Пользователь {created_user.username} успешно зарегистрирован",
            success=True
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        print(f"Registration error: {str(e)}")  # Debug logging
        import traceback
        traceback.print_exc()  # Debug traceback
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при регистрации пользователя: {str(e)}"
        )


@router.post("/login", response_model=TokenResponse)
async def login_user(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Авторизация пользователя.
    
    - **email**: Email пользователя
    - **password**: Пароль пользователя
    
    Возвращает access и refresh токены.
    """
    user = auth_service.authenticate_user(db, request.email, request.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    tokens = auth_service.create_tokens_for_user(db, user)
    return tokens


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Обновление access токена по refresh токену.
    
    - **refresh_token**: Действующий refresh токен
    
    Возвращает новую пару токенов.
    """
    tokens = auth_service.refresh_access_token(db, request.refresh_token)
    
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный refresh токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return tokens


@router.post("/logout", response_model=AuthResponse)
async def logout_user(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Выход из системы (отзыв всех токенов пользователя).
    
    Требует авторизации.
    """
    try:
        # Отзываем все токены пользователя
        from app.database.crud import token as token_crud
        revoked_count = token_crud.revoke_all_user_tokens(db, user_id=current_user.id)
        
        return AuthResponse(
            message=f"Выход выполнен успешно. Отозвано токенов: {revoked_count}",
            success=True
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при выходе из системы"
        )


@router.get("/me", response_model=UserProfileResponse)
async def get_current_user_profile(
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Получение профиля текущего пользователя.
    
    Требует авторизации.
    """
    return UserProfileResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        created_at=current_user.created_at.isoformat()
    )


@router.post("/verify", response_model=AuthResponse)
async def verify_token(
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Проверка валидности токена.
    
    Требует авторизации.
    """
    return AuthResponse(
        message=f"Токен валиден для пользователя {current_user.username}",
        success=True
    )
