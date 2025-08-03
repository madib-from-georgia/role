"""
CRUD операции для пользователей.
"""

from typing import Optional
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.database.crud.base import CRUDBase
from app.database.models.user import User
from app.schemas.user import UserCreate, UserUpdate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """CRUD операции для модели User."""

    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """Получение пользователя по email."""
        return db.query(User).filter(User.email == email).first()

    def get_by_username(self, db: Session, *, username: str) -> Optional[User]:
        """Получение пользователя по username."""
        return db.query(User).filter(User.username == username).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        """Создание пользователя с хешированием пароля."""
        db_obj = User(
            email=obj_in.email,
            username=obj_in.username,
            password_hash=self.get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            is_active=obj_in.is_active,
        )
        db.add(db_obj)
        try:
            db.commit()
            db.refresh(db_obj)
        except Exception as e:
            db.rollback()
            raise ValueError(f"Ошибка создания пользователя: {str(e)}")
        return db_obj

    def update(self, db: Session, *, db_obj: User, obj_in: UserUpdate) -> User:
        """Обновление пользователя с возможностью смены пароля."""
        update_data = obj_in.dict(exclude_unset=True)
        
        if "password" in update_data:
            hashed_password = self.get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["password_hash"] = hashed_password
        
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        """Аутентификация пользователя."""
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not self.verify_password(password, user.password_hash):
            return None
        return user

    def is_active(self, user: User) -> bool:
        """Проверка активности пользователя."""
        return user.is_active

    def get_password_hash(self, password: str) -> str:
        """Получение хеша пароля."""
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Проверка пароля."""
        return pwd_context.verify(plain_password, hashed_password)

    def deactivate(self, db: Session, *, db_obj: User) -> User:
        """Деактивация пользователя."""
        db_obj.is_active = False
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def activate(self, db: Session, *, db_obj: User) -> User:
        """Активация пользователя."""
        db_obj.is_active = True
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


user = CRUDUser(User)
