"""
Pydantic схемы для чеклистов.
"""

from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class ChecklistResponseBase(BaseModel):
    """Базовая схема ответа чеклиста."""
    checklist_type: str = Field(..., min_length=1, max_length=50)
    question_id: str = Field(..., min_length=1, max_length=100)
    response: Optional[str] = Field(None, max_length=5000)
    confidence_level: int = Field(default=3, ge=1, le=5)


class ChecklistResponseCreate(ChecklistResponseBase):
    """Схема для создания ответа чеклиста."""
    character_id: int


class ChecklistResponseUpdate(BaseModel):
    """Схема для обновления ответа чеклиста."""
    response: Optional[str] = Field(None, max_length=5000)
    confidence_level: Optional[int] = Field(None, ge=1, le=5)


class ChecklistResponseInDBBase(ChecklistResponseBase):
    """Базовая схема ответа чеклиста в БД."""
    id: int
    character_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ChecklistResponse(ChecklistResponseInDBBase):
    """Схема ответа чеклиста для API."""
    pass


class ChecklistModule(BaseModel):
    """Схема модуля чеклиста."""
    id: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1, max_length=1000)
    questions: list[str] = []


class ChecklistQuestion(BaseModel):
    """Схема вопроса чеклиста."""
    id: str = Field(..., min_length=1, max_length=100)
    text: str = Field(..., min_length=1, max_length=1000)
    type: str = Field(default="text")  # text, textarea, select, radio
    options: Optional[list[str]] = None
    required: bool = True
    help_text: Optional[str] = None
