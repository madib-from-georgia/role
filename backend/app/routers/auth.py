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
    UserProfileResponse,
    ChangePasswordRequest,
    UpdateProfileRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest
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


@router.put("/me", response_model=UserProfileResponse)
async def update_user_profile(
    request: UpdateProfileRequest,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Обновление профиля текущего пользователя.
    
    Требует авторизации.
    """
    try:
        from app.database.crud import user as user_crud
        from app.schemas.user import UserUpdate
        
        # Проверяем уникальность email и username, если они изменяются
        update_data = request.dict(exclude_unset=True)
        
        if update_data.get("email") and update_data["email"] != current_user.email:
            existing_user = user_crud.get_by_email(db, email=update_data["email"])
            if existing_user and existing_user.id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Пользователь с таким email уже существует"
                )
        
        if update_data.get("username") and update_data["username"] != current_user.username:
            existing_user = user_crud.get_by_username(db, username=update_data["username"])
            if existing_user and existing_user.id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Пользователь с таким username уже существует"
                )
        
        # Обновляем пользователя
        user_update = UserUpdate(**update_data)
        updated_user = user_crud.update(db, db_obj=current_user, obj_in=user_update)
        
        return UserProfileResponse(
            id=updated_user.id,
            email=updated_user.email,
            username=updated_user.username,
            full_name=updated_user.full_name,
            is_active=updated_user.is_active,
            created_at=updated_user.created_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка обновления профиля: {str(e)}"
        )


@router.post("/change-password", response_model=AuthResponse)
async def change_password(
    request: ChangePasswordRequest,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Смена пароля текущего пользователя.
    
    Требует авторизации и подтверждения текущего пароля.
    """
    try:
        from app.database.crud import user as user_crud
        from app.schemas.user import UserUpdate
        
        # Проверяем текущий пароль
        if not user_crud.verify_password(request.current_password, current_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверный текущий пароль"
            )
        
        # Проверяем, что новый пароль отличается от текущего
        if user_crud.verify_password(request.new_password, current_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Новый пароль должен отличаться от текущего"
            )
        
        # Обновляем пароль
        user_update = UserUpdate(password=request.new_password)
        user_crud.update(db, db_obj=current_user, obj_in=user_update)
        
        # Отзываем все токены пользователя для безопасности
        from app.database.crud import token as token_crud
        revoked_count = token_crud.revoke_all_user_tokens(db, user_id=current_user.id)
        
        return AuthResponse(
            message=f"Пароль успешно изменен. Отозвано токенов: {revoked_count}. Войдите в систему заново.",
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка смены пароля: {str(e)}"
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


@router.post("/forgot-password", response_model=AuthResponse)
async def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Запрос на сброс пароля.
    
    - **email**: Email пользователя
    
    Отправляет email с ссылкой для сброса пароля.
    """
    try:
        # Ищем пользователя по email
        user = auth_service.get_user_by_email(db, email=request.email)
        
        if not user:
            # Не раскрываем информацию о том, существует ли пользователь
            return AuthResponse(
                message="Если пользователь с таким email существует, на него будет отправлено письмо с инструкциями по сбросу пароля.",
                success=True
            )
        
        if not user.is_active:
            return AuthResponse(
                message="Если пользователь с таким email существует, на него будет отправлено письмо с инструкциями по сбросу пароля.",
                success=True
            )
        
        # Создаем токен для сброса пароля
        reset_token = auth_service.create_password_reset_token(db, user)
        
        # Отправляем email
        from app.services.email import email_service
        email_sent = email_service.send_password_reset_email(
            to_email=user.email,
            reset_token=reset_token,
            user_name=user.full_name or user.username
        )
        
        if not email_sent:
            # Логируем ошибку, но не показываем пользователю
            print(f"Failed to send password reset email to {user.email}")
        
        return AuthResponse(
            message="Если пользователь с таким email существует, на него будет отправлено письмо с инструкциями по сбросу пароля.",
            success=True
        )
        
    except Exception as e:
        print(f"Forgot password error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при обработке запроса на сброс пароля"
        )


@router.post("/reset-password", response_model=AuthResponse)
async def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Сброс пароля по токену.
    
    - **token**: Токен для сброса пароля из email
    - **new_password**: Новый пароль (минимум 8 символов)
    
    Устанавливает новый пароль и отзывает все токены пользователя.
    """
    try:
        # Сбрасываем пароль
        success = auth_service.reset_password_with_token(
            db,
            token=request.token,
            new_password=request.new_password
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверный или истекший токен сброса пароля"
            )
        
        # Получаем пользователя для отправки уведомления
        user = auth_service.verify_password_reset_token(db, request.token)
        if user:
            # Отправляем уведомление об успешной смене пароля
            from app.services.email import email_service
            email_service.send_password_changed_notification(
                to_email=user.email,
                user_name=user.full_name or user.username
            )
        
        return AuthResponse(
            message="Пароль успешно изменен. Войдите в систему с новым паролем.",
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Reset password error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при сбросе пароля"
        )
