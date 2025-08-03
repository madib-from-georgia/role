"""
Pydantic схемы для текста произведения.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class TextBase(BaseModel):
    """Базовая схема текста."""
    filename: str = Field(..., min_length=1, max_length=255)
    original_format: str = Field(..., pattern="^(txt|pdf|fb2|epub)$")
    content: Optional[str] = None
    file_metadata: Optional[Dict[str, Any]] = None


class TextCreate(TextBase):
    """Схема для создания текста."""
    project_id: int


class TextUpdate(BaseModel):
    """Схема для обновления текста."""
    filename: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = None
    file_metadata: Optional[Dict[str, Any]] = None
    processed_at: Optional[datetime] = None


class TextInDBBase(TextBase):
    """Базовая схема текста в БД."""
    id: int
    project_id: int
    processed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class Text(TextInDBBase):
    """Схема текста для API."""
    pass


class TextWithCharacters(Text):
    """Схема текста с персонажами."""
    characters: List["Character"] = []
