"""
Pydantic схемы для чеклистов
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class SourceType(str, Enum):
    """Источник ответа на вопрос"""
    FOUND_IN_TEXT = "FOUND_IN_TEXT"
    LOGICALLY_DERIVED = "LOGICALLY_DERIVED"
    IMAGINED = "IMAGINED"


# Схемы для ответов на вопросы
class ChecklistAnswerBase(BaseModel):
    external_id: str = Field(..., description="Идентификатор из JSON")
    value_male: str = Field(..., description="Значение для мужского пола")
    value_female: str = Field(..., description="Значение для женского пола")
    exported_value_male: Optional[str] = Field(None, description="Экспортируемое значение для мужского пола")
    exported_value_female: Optional[str] = Field(None, description="Экспортируемое значение для женского пола")
    hint: Optional[str] = Field(None, description="Подсказка для актера")
    order_index: int = Field(0, description="Порядок отображения")


class ChecklistAnswer(ChecklistAnswerBase):
    id: int
    question_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Базовые схемы для вопросов
class ChecklistQuestionBase(BaseModel):
    external_id: str = Field(..., description="Идентификатор из JSON")
    text: str = Field(..., description="Текст вопроса")
    order_index: int = Field(0, description="Порядок отображения")
    answer_type: str = Field("single", description="Тип ответа: single, multiple")
    source_type: Optional[str] = Field(None, description="Источник ответа: text, logic, imagination")


class ChecklistQuestion(ChecklistQuestionBase):
    id: int
    question_group_id: int
    answers: List[ChecklistAnswer] = []
    created_at: datetime
    
    class Config:
        from_attributes = True


# Базовые схемы для групп вопросов
class ChecklistQuestionGroupBase(BaseModel):
    external_id: str = Field(..., description="Идентификатор из JSON")
    title: str = Field(..., description="Название группы вопросов")
    order_index: int = Field(0, description="Порядок отображения")


class ChecklistQuestionGroup(ChecklistQuestionGroupBase):
    id: int
    subsection_id: int
    questions: List[ChecklistQuestion] = []
    
    class Config:
        from_attributes = True


# Базовые схемы для подсекций
class ChecklistSubsectionBase(BaseModel):
    external_id: str = Field(..., description="Идентификатор из JSON")
    title: str = Field(..., description="Название подсекции")
    number: Optional[str] = Field(None, description="Номер подсекции")
    order_index: int = Field(0, description="Порядок отображения")


class ChecklistSubsection(ChecklistSubsectionBase):
    id: int
    section_id: int
    question_groups: List[ChecklistQuestionGroup] = []
    
    class Config:
        from_attributes = True


# Базовые схемы для секций
class ChecklistSectionBase(BaseModel):
    external_id: str = Field(..., description="Идентификатор из JSON")
    title: str = Field(..., description="Название секции")
    number: Optional[str] = Field(None, description="Номер секции")
    icon: Optional[str] = Field(None, description="Иконка секции")
    order_index: int = Field(0, description="Порядок отображения")


class ChecklistSection(ChecklistSectionBase):
    id: int
    checklist_id: int
    subsections: List[ChecklistSubsection] = []
    
    class Config:
        from_attributes = True


# Базовые схемы для чеклистов
class ChecklistBase(BaseModel):
    external_id: str = Field(..., description="Идентификатор из JSON")
    title: str = Field(..., description="Название чеклиста")
    description: Optional[str] = Field(None, description="Описание чеклиста")
    slug: str = Field(..., description="URL slug")
    icon: Optional[str] = Field(None, description="Иконка чеклиста")
    order_index: int = Field(0, description="Порядок отображения")
    is_active: bool = Field(True, description="Активен ли чеклист")
    goal: Optional[str] = Field(None, description="Цель чеклиста")
    file_hash: Optional[str] = Field(None, description="SHA-256 хеш JSON файла")
    version: Optional[str] = Field(None, description="Версия чеклиста")


class ChecklistCreate(ChecklistBase):
    pass


class ChecklistUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    order_index: Optional[int] = None
    is_active: Optional[bool] = None
    goal: Optional[str] = None


class Checklist(ChecklistBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    sections: List[ChecklistSection] = []
    completion_stats: Optional[dict] = Field(None, description="Статистика заполнения")
    
    class Config:
        from_attributes = True


# Схемы для ответов
class ChecklistResponseBase(BaseModel):
    answer_id: Optional[int] = Field(None, description="ID выбранного ответа")
    answer_text: Optional[str] = Field(None, description="Текстовый ответ (для свободного ввода)")
    comment: Optional[str] = Field(None, description="Комментарий к ответу")


class ChecklistResponseCreate(ChecklistResponseBase):
    question_id: int = Field(..., description="ID вопроса")
    character_id: int = Field(..., description="ID персонажа")
    source_type: Optional[SourceType] = Field(None, description="Источник ответа")


class ChecklistResponseUpdate(BaseModel):
    answer_id: Optional[int] = Field(None, description="ID выбранного ответа")
    answer_text: Optional[str] = Field(None, description="Текстовый ответ (для свободного ввода)")
    comment: Optional[str] = Field(None, description="Комментарий к ответу")
    source_type: Optional[SourceType] = Field(None, description="Источник ответа")
    change_reason: Optional[str] = Field(None, description="Причина изменения")


class ChecklistResponse(ChecklistResponseBase):
    id: int
    question_id: int
    character_id: int
    answer: Optional[ChecklistAnswer] = None
    source_type: Optional[SourceType]
    is_current: bool
    version: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ChecklistResponseHistory(BaseModel):
    id: int
    response_id: int
    previous_answer: Optional[str]
    previous_source_type: Optional[SourceType]
    previous_comment: Optional[str]
    previous_version: Optional[int]
    change_reason: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Схемы с ответами
class ChecklistQuestionWithResponse(ChecklistQuestion):
    current_response: Optional[ChecklistResponse] = None
    response_history: List[ChecklistResponseHistory] = []


class ChecklistQuestionGroupWithResponses(ChecklistQuestionGroup):
    questions: List[ChecklistQuestionWithResponse] = []


class ChecklistSubsectionWithResponses(ChecklistSubsection):
    question_groups: List[ChecklistQuestionGroupWithResponses] = []


class ChecklistSectionWithResponses(ChecklistSection):
    subsections: List[ChecklistSubsectionWithResponses] = []


class ChecklistWithResponses(Checklist):
    sections: List[ChecklistSectionWithResponses] = []
    completion_stats: Optional[dict] = Field(None, description="Статистика заполнения")


# Статистика
class ChecklistStats(BaseModel):
    checklist_id: int = Field(..., description="ID чеклиста")
    total_questions: int = Field(..., description="Общее количество вопросов")
    answered_questions: int = Field(..., description="Количество отвеченных вопросов")
    completion_percentage: float = Field(..., description="Процент заполнения")
    answers_by_source: dict = Field(..., description="Распределение ответов по источникам")
    last_updated: Optional[datetime] = Field(None, description="Последнее обновление")


# Массовые операции
class BulkResponseUpdate(BaseModel):
    responses: List[ChecklistResponseUpdate] = Field(..., description="Список обновлений ответов")
    character_id: int = Field(..., description="ID персонажа")


class RestoreResponseVersion(BaseModel):
    response_id: int = Field(..., description="ID ответа")
    history_id: int = Field(..., description="ID версии для восстановления")
    restore_reason: Optional[str] = Field(None, description="Причина восстановления")
