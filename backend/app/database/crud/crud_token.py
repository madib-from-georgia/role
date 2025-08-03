"""
CRUD операции для JWT токенов.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.database.crud.base import CRUDBase
from app.database.models.token import UserToken
from app.schemas.token import TokenCreate, TokenUpdate


class CRUDToken(CRUDBase[UserToken, TokenCreate, TokenUpdate]):
    """CRUD операции для модели UserToken."""

    def get_by_token_hash(self, db: Session, *, token_hash: str) -> Optional[UserToken]:
        """Получение токена по хешу."""
        return (
            db.query(UserToken)
            .filter(UserToken.token_hash == token_hash)
            .filter(UserToken.is_revoked == False)
            .first()
        )

    def get_active_tokens_by_user(
        self, db: Session, *, user_id: int, token_type: str = None
    ) -> List[UserToken]:
        """Получение активных токенов пользователя."""
        query = (
            db.query(self.model)
            .filter(UserToken.user_id == user_id)
            .filter(UserToken.is_revoked == False)
            .filter(UserToken.expires_at > datetime.utcnow())
        )
        
        if token_type:
            query = query.filter(UserToken.token_type == token_type)
        
        return query.all()

    def get_expired_tokens(self, db: Session) -> List[UserToken]:
        """Получение истекших токенов."""
        return (
            db.query(self.model)
            .filter(UserToken.expires_at <= datetime.utcnow())
            .filter(UserToken.is_revoked == False)
            .all()
        )

    def revoke_token(self, db: Session, *, token_hash: str) -> Optional[UserToken]:
        """Отзыв токена."""
        token = self.get_by_token_hash(db, token_hash=token_hash)
        if not token:
            return None
        
        token.is_revoked = True
        db.add(token)
        db.commit()
        db.refresh(token)
        return token

    def revoke_all_user_tokens(
        self, db: Session, *, user_id: int, token_type: str = None
    ) -> int:
        """Отзыв всех токенов пользователя."""
        query = (
            db.query(self.model)
            .filter(UserToken.user_id == user_id)
            .filter(UserToken.is_revoked == False)
        )
        
        if token_type:
            query = query.filter(UserToken.token_type == token_type)
        
        count = query.count()
        query.update({"is_revoked": True})
        db.commit()
        return count

    def cleanup_expired_tokens(self, db: Session) -> int:
        """Очистка истекших токенов."""
        expired_tokens = self.get_expired_tokens(db)
        count = len(expired_tokens)
        
        for token in expired_tokens:
            db.delete(token)
        
        db.commit()
        return count

    def is_token_valid(self, db: Session, *, token_hash: str) -> bool:
        """Проверка валидности токена."""
        token = self.get_by_token_hash(db, token_hash=token_hash)
        if not token:
            return False
        
        return (
            not token.is_revoked and 
            token.expires_at > datetime.utcnow()
        )

    def get_token_info(self, db: Session, *, token_hash: str) -> Optional[dict]:
        """Получение информации о токене."""
        token = self.get_by_token_hash(db, token_hash=token_hash)
        if not token:
            return None
        
        return {
            "user_id": token.user_id,
            "token_type": token.token_type,
            "expires_at": token.expires_at,
            "is_valid": self.is_token_valid(db, token_hash=token_hash),
            "created_at": token.created_at
        }

    def count_active_tokens_by_user(self, db: Session, *, user_id: int) -> int:
        """Подсчет активных токенов пользователя."""
        return (
            db.query(self.model)
            .filter(UserToken.user_id == user_id)
            .filter(UserToken.is_revoked == False)
            .filter(UserToken.expires_at > datetime.utcnow())
            .count()
        )

    def get_refresh_token_by_user(self, db: Session, *, user_id: int) -> Optional[UserToken]:
        """Получение активного refresh токена пользователя."""
        return (
            db.query(self.model)
            .filter(UserToken.user_id == user_id)
            .filter(UserToken.token_type == "refresh")
            .filter(UserToken.is_revoked == False)
            .filter(UserToken.expires_at > datetime.utcnow())
            .order_by(UserToken.created_at.desc())
            .first()
        )


token = CRUDToken(UserToken)
