"""
Модель проекта.
"""

from sqlalchemy import Column, String, Text, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.database.models.base import BaseModel


class Project(BaseModel):
    """Модель проекта пользователя."""
    
    __tablename__ = "projects"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="projects")
    texts = relationship("Text", back_populates="project", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Project(id={self.id}, title='{self.title}', user_id={self.user_id})>"