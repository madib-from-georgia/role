"""
Модель персонажа.
"""

from sqlalchemy import Column, String, Integer, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from app.database.models.base import BaseModel


class Character(BaseModel):
    """Модель персонажа из произведения."""
    
    __tablename__ = "characters"
    
    text_id = Column(Integer, ForeignKey("texts.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    aliases = Column(JSON, nullable=True)  # Альтернативные имена и прозвища
    importance_score = Column(Float, nullable=True)  # Оценка важности персонажа (0-1)
    speech_attribution = Column(JSON, nullable=True)  # Атрибуция речи от NLP
    
    # Relationships
    text = relationship("Text", back_populates="characters")
    checklist_responses = relationship(
        "ChecklistResponse", 
        back_populates="character", 
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<Character(id={self.id}, name='{self.name}', text_id={self.text_id})>"
