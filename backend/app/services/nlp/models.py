"""
Модели данных для NLP анализа
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum


class SpeechType(str, Enum):
    """Типы речи персонажей"""
    DIALOGUE = "dialogue"
    MONOLOGUE = "monologue"
    INTERNAL = "internal"
    AUTHOR = "author"


class Gender(str, Enum):
    """Пол персонажа"""
    MALE = "male"
    FEMALE = "female"
    UNKNOWN = "unknown"


class CharacterData(BaseModel):
    """
    Данные персонажа, извлеченные из текста
    """
    name: str = Field(..., description="Имя персонажа")
    aliases: List[str] = Field(default_factory=list, description="Альтернативные имена")
    description: Optional[str] = Field(None, description="Описание персонажа из текста")
    mentions_count: int = Field(0, description="Количество упоминаний")
    first_mention_position: int = Field(0, description="Позиция первого упоминания")
    importance_score: float = Field(0.0, description="Оценка важности персонажа (0.0-1.0)")
    source: str = Field(..., description="Источник извлечения (character_list, dialogue, etc.)")
    gender: Gender = Field(default=Gender.UNKNOWN, description="Пол персонажа")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Иван Иванович Иванов",
                "aliases": ["Иван", "Ваня"],
                "description": "купец, 45 лет",
                "mentions_count": 12,
                "first_mention_position": 150,
                "importance_score": 0.85,
                "source": "character_list",
                "gender": "male"
            }
        }


class SpeechData(BaseModel):
    """
    Данные о речи персонажа
    """
    character_name: str = Field(..., description="Имя персонажа")
    text: str = Field(..., description="Текст речи")
    position: int = Field(..., description="Позиция в тексте")
    speech_type: SpeechType = Field(default=SpeechType.DIALOGUE, description="Тип речи")
    confidence: float = Field(1.0, description="Уверенность в атрибуции (0.0-1.0)")
    context: Optional[str] = Field(None, description="Контекст речи")
    
    class Config:
        json_schema_extra = {
            "example": {
                "character_name": "Иван Иванович",
                "text": "Да здравствует наша великая страна!",
                "position": 1250,
                "speech_type": "dialogue",
                "confidence": 1.0,
                "context": "В сцене на площади"
            }
        }


class ExtractionStats(BaseModel):
    """
    Статистика извлечения данных
    """
    method_used: str = Field(..., description="Метод извлечения")
    is_play_format: bool = Field(..., description="Является ли текст пьесой")
    has_character_section: bool = Field(..., description="Есть ли секция персонажей")
    total_characters: int = Field(..., description="Общее количество персонажей")
    total_speech_attributions: int = Field(..., description="Общее количество атрибуций речи")
    extraction_time: float = Field(..., description="Время извлечения (секунды)")
    text_length: int = Field(..., description="Длина обработанного текста")
    processing_errors: List[str] = Field(default_factory=list, description="Ошибки обработки")


class NLPResult(BaseModel):
    """
    Результат NLP анализа текста
    """
    text_id: int = Field(..., description="ID обработанного текста")
    characters: List[CharacterData] = Field(default_factory=list, description="Найденные персонажи")
    speech_attributions: List[SpeechData] = Field(default_factory=list, description="Атрибуции речи")
    extraction_stats: ExtractionStats = Field(..., description="Статистика извлечения")
    
    def get_character_by_name(self, name: str) -> Optional[CharacterData]:
        """Поиск персонажа по имени"""
        for character in self.characters:
            if character.name == name or name in character.aliases:
                return character
        return None
    
    def get_main_characters(self, min_importance: float = 0.3) -> List[CharacterData]:
        """Получение главных персонажей по важности"""
        return [char for char in self.characters if char.importance_score >= min_importance]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Получение общей статистики"""
        return {
            "total_characters": len(self.characters),
            "main_characters": len(self.get_main_characters()),
            "total_speech_attributions": len(self.speech_attributions),
            "average_importance": sum(c.importance_score for c in self.characters) / len(self.characters) if self.characters else 0,
            "extraction_method": self.extraction_stats.method_used,
            "is_play_format": self.extraction_stats.is_play_format,
            "processing_time": self.extraction_stats.extraction_time
        }
    
    class Config:
        json_schema_extra = {
            "example": {
                "text_id": 123,
                "characters": [
                    {
                        "name": "Иван Иванович",
                        "aliases": ["Иван"],
                        "mentions_count": 15,
                        "importance_score": 0.9,
                        "source": "character_list"
                    }
                ],
                "speech_attributions": [
                    {
                        "character_name": "Иван Иванович",
                        "text": "Добро пожаловать!",
                        "position": 500,
                        "speech_type": "dialogue"
                    }
                ]
            }
        }