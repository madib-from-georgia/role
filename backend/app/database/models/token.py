"""
Модель JWT токена.
"""

from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database.models.base import BaseModel


class UserToken(BaseModel):
    """Модель для хранения JWT токенов."""
    
    __tablename__ = "user_tokens"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token_hash = Column(String(255), nullable=False, index=True)
    token_type = Column(String(20), default="access", nullable=False)  # access, refresh, password_reset
    expires_at = Column(DateTime, nullable=False)
    is_revoked = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="tokens")
    
    def __repr__(self):
        return f"<UserToken(id={self.id}, user_id={self.user_id}, type='{self.token_type}')>"
