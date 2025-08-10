"""
Модель текста произведения.
"""

from sqlalchemy import Column, String, Text, Integer, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from app.database.models.base import BaseModel


class Text(BaseModel):
    """Модель загруженного текста произведения."""
    
    __tablename__ = "texts"
    
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String(255), nullable=False)
    original_format = Column(String(10), nullable=False)  # txt, pdf, fb2, epub
    content = Column(Text, nullable=True)  # Извлеченный текст
    file_metadata = Column(JSON, nullable=True)  # Метаданные файла (автор, название и т.д.)
    processed_at = Column(DateTime, nullable=True)  # Время обработки NLP
    
    # Relationships
    project = relationship("Project", back_populates="texts")
    characters = relationship("Character", back_populates="text", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Text(id={self.id}, filename='{self.filename}', format='{self.original_format}')>"