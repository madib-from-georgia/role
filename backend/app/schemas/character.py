"""
Pydantic схемы для персонажа.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class Gender(str, Enum):
    """Перечисление полов персонажа."""
    MALE = "male"
    FEMALE = "female"
    UNKNOWN = "unknown"


class CharacterBase(BaseModel):
    """Базовая схема персонажа."""
    name: str = Field(..., min_length=1, max_length=255)
    aliases: Optional[List[str]] = None
    importance_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    speech_attribution: Optional[Dict[str, Any]] = None
    gender: Optional[Gender] = Field(None, description="Пол персонажа")


class CharacterCreate(CharacterBase):
    """Схема для создания персонажа."""
    text_id: int


class CharacterUpdate(BaseModel):
    """Схема для обновления персонажа."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    aliases: Optional[List[str]] = None
    importance_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    speech_attribution: Optional[Dict[str, Any]] = None
    gender: Optional[Gender] = Field(None, description="Пол персонажа")


class CharacterInDBBase(CharacterBase):
    """Базовая схема персонажа в БД."""
    id: int
    text_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class Character(CharacterInDBBase):
    """Схема персонажа для API."""
    pass


class CharacterWithResponses(Character):
    """Схема персонажа с ответами чеклистов."""
    checklist_responses: List["ChecklistResponse"] = []
