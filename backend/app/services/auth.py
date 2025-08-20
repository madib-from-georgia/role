"""
JWT авторизация и управление токенами.
"""

import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.database.crud import user as user_crud, token as token_crud
from app.database.models.user import User
from app.schemas.token import TokenCreate, TokenResponse
from app.schemas.user import UserCreate


class AuthService:
    """Сервис для управления авторизацией и JWT токенами."""
    
    def __init__(self):
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 15
        self.refresh_token_expire_days = 7
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Создание access токена."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Создание refresh токена."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Проверка и декодирование токена."""
        try:
            payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            return None
    
    def get_token_hash(self, token: str) -> str:
        """Получение хеша токена для хранения в БД."""
        import hashlib
        return hashlib.sha256(token.encode()).hexdigest()
    
    def register_user(self, db: Session, user_data: UserCreate) -> User:
        """Регистрация нового пользователя."""
        # Проверяем, что пользователь не существует
        existing_user = user_crud.get_by_email(db, email=user_data.email)
        if existing_user:
            raise ValueError("Пользователь с таким email уже существует")
        
        existing_username = user_crud.get_by_username(db, username=user_data.username)
        if existing_username:
            raise ValueError("Пользователь с таким username уже существует")
        
        # Создаем пользователя
        created_user = user_crud.create(db, obj_in=user_data)
        return created_user
    
    def authenticate_user(self, db: Session, email: str, password: str) -> Optional[User]:
        """Аутентификация пользователя."""
        user = user_crud.authenticate(db, email=email, password=password)
        if not user:
            return None
        if not user_crud.is_active(user):
            return None
        return user
    
    def create_tokens_for_user(self, db: Session, user: User) -> TokenResponse:
        """Создание пары токенов для пользователя."""
        # Отзываем все старые токены пользователя
        token_crud.revoke_all_user_tokens(db, user_id=user.id)
        
        # Создаем новые токены
        access_token_data = {"sub": str(user.id), "username": user.username}
        refresh_token_data = {"sub": str(user.id), "username": user.username}
        
        access_token = self.create_access_token(access_token_data)
        refresh_token = self.create_refresh_token(refresh_token_data)
        
        # Сохраняем токены в БД
        access_token_hash = self.get_token_hash(access_token)
        refresh_token_hash = self.get_token_hash(refresh_token)
        
        access_expires = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        refresh_expires = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        
        # Сохраняем access token
        access_token_data = {
            "user_id": user.id,
            "token_hash": access_token_hash,
            "token_type": "access",
            "expires_at": access_expires
        }
        token_crud.create(db, obj_in=access_token_data)
        
        # Сохраняем refresh token
        refresh_token_data = {
            "user_id": user.id,
            "token_hash": refresh_token_hash,
            "token_type": "refresh",
            "expires_at": refresh_expires
        }
        token_crud.create(db, obj_in=refresh_token_data)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=self.access_token_expire_minutes * 60
        )
    
    def refresh_access_token(self, db: Session, refresh_token: str) -> Optional[TokenResponse]:
        """Обновление access токена по refresh токену."""
        # Проверяем refresh токен
        payload = self.verify_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            return None
        
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        # Проверяем, что токен не отозван в БД
        refresh_token_hash = self.get_token_hash(refresh_token)
        if not token_crud.is_token_valid(db, token_hash=refresh_token_hash):
            return None
        
        # Получаем пользователя
        user = user_crud.get(db, id=int(user_id))
        if not user or not user_crud.is_active(user):
            return None
        
        # Создаем новую пару токенов
        return self.create_tokens_for_user(db, user)
    
    def logout_user(self, db: Session, access_token: str) -> bool:
        """Выход пользователя (отзыв всех токенов)."""
        payload = self.verify_token(access_token)
        if not payload:
            return False
        
        user_id = payload.get("sub")
        if not user_id:
            return False
        
        # Отзываем все токены пользователя
        revoked_count = token_crud.revoke_all_user_tokens(db, user_id=int(user_id))
        return revoked_count > 0
    
    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """Получение пользователя по email."""
        return user_crud.get_by_email(db, email=email)
    
    def get_current_user(self, db: Session, token: str) -> Optional[User]:
        """Получение текущего пользователя по токену."""
        payload = self.verify_token(token)
        if not payload:
            return None
        
        user_id = payload.get("sub")
        username = payload.get("username")
        
        if not user_id:
            return None
        
        # Проверяем, что токен не отозван в БД
        token_hash = self.get_token_hash(token)
        if not token_crud.is_token_valid(db, token_hash=token_hash):
            return None
        
        # Получаем пользователя
        user = user_crud.get(db, id=int(user_id))
        if not user or not user_crud.is_active(user):
            return None
        
        # Проверяем соответствие username
        if user.username != username:
            return None
        
        return user
    
    def cleanup_expired_tokens(self, db: Session) -> int:
        """Очистка истекших токенов."""
        return token_crud.cleanup_expired_tokens(db)
    
    def create_password_reset_token(self, db: Session, user: User) -> str:
        """Создание токена для сброса пароля."""
        from app.services.email import email_service
        
        # Отзываем все старые токены сброса пароля для пользователя
        token_crud.revoke_user_tokens_by_type(db, user_id=user.id, token_type="password_reset")
        
        # Генерируем новый токен
        reset_token = email_service.generate_reset_token()
        token_hash = self.get_token_hash(reset_token)
        
        # Токен действителен 1 час
        expires_at = datetime.utcnow() + timedelta(hours=1)
        
        # Сохраняем токен в БД
        token_data = {
            "user_id": user.id,
            "token_hash": token_hash,
            "token_type": "password_reset",
            "expires_at": expires_at
        }
        token_crud.create(db, obj_in=token_data)
        
        return reset_token
    
    def verify_password_reset_token(self, db: Session, token: str) -> Optional[User]:
        """Проверка токена сброса пароля и получение пользователя."""
        token_hash = self.get_token_hash(token)
        
        # Проверяем, что токен существует и не истек
        db_token = token_crud.get_valid_token_by_hash(db, token_hash=token_hash, token_type="password_reset")
        if not db_token:
            return None
        
        # Получаем пользователя
        user = user_crud.get(db, id=db_token.user_id)
        if not user or not user_crud.is_active(user):
            return None
        
        return user
    
    def reset_password_with_token(self, db: Session, token: str, new_password: str) -> bool:
        """Сброс пароля по токену."""
        # Проверяем токен и получаем пользователя
        user = self.verify_password_reset_token(db, token)
        if not user:
            return False
        
        # Обновляем пароль
        from app.schemas.user import UserUpdate
        user_update = UserUpdate(password=new_password)
        user_crud.update(db, db_obj=user, obj_in=user_update)
        
        # Отзываем токен сброса пароля
        token_hash = self.get_token_hash(token)
        token_crud.revoke_token_by_hash(db, token_hash=token_hash)
        
        # Отзываем все JWT токены пользователя для безопасности
        token_crud.revoke_all_user_tokens(db, user_id=user.id)
        
        return True


# Глобальный экземпляр сервиса
auth_service = AuthService()
