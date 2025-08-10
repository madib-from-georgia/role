"""
Базовые модели для SQLAlchemy.
"""

from sqlalchemy import Column, Integer, DateTime, func
from app.database.connection import Base


class TimestampMixin:
    """Mixin для добавления временных меток."""
    
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)


class BaseModel(Base, TimestampMixin):
    """Базовая модель с ID и временными метками."""
    
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
