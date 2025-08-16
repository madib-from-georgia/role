"""
Модель персонажа.
"""

from sqlalchemy import Column, String, Integer, ForeignKey, Float, JSON, Enum
from sqlalchemy.orm import relationship
from app.database.models.base import BaseModel
import enum


class GenderEnum(str, enum.Enum):
    """Перечисление полов персонажа."""
    MALE = "male"
    FEMALE = "female"
    UNKNOWN = "unknown"


class Character(BaseModel):
    """Модель персонажа из произведения."""
    
    __tablename__ = "characters"
    
    text_id = Column(Integer, ForeignKey("texts.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    aliases = Column(JSON, nullable=True)  # Альтернативные имена и прозвища
    importance_score = Column(Float, nullable=True)  # Оценка важности персонажа (0-1)
    speech_attribution = Column(JSON, nullable=True)  # Атрибуция речи от NLP
    gender = Column(Enum(GenderEnum), nullable=True, default=GenderEnum.UNKNOWN)  # Пол персонажа
    sort_order = Column(Integer, nullable=True, default=0)  # Порядок сортировки для drag-and-drop
    
    # Relationships
    text = relationship("Text", back_populates="characters")
    checklist_responses = relationship(
        "ChecklistResponse", 
        back_populates="character", 
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<Character(id={self.id}, name='{self.name}', text_id={self.text_id})>"
