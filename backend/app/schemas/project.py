"""
Pydantic схемы для проекта.
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class ProjectBase(BaseModel):
    """Базовая схема проекта."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)


class ProjectCreate(ProjectBase):
    """Схема для создания проекта."""
    pass


class ProjectUpdate(BaseModel):
    """Схема для обновления проекта."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)


class ProjectInDBBase(ProjectBase):
    """Базовая схема проекта в БД."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class Project(ProjectInDBBase):
    """Схема проекта для API."""
    pass


class ProjectWithTexts(Project):
    """Схема проекта с текстами."""
    texts: List["Text"] = []
