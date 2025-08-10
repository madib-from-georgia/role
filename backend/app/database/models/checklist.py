"""
Модели базы данных для системы чеклистов
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from .base import BaseModel
from .character import Character


class SourceType(enum.Enum):
    """Источник ответа на вопрос"""
    FOUND_IN_TEXT = "FOUND_IN_TEXT"        # найдено в тексте
    LOGICALLY_DERIVED = "LOGICALLY_DERIVED"  # логически выведено
    IMAGINED = "IMAGINED"                   # придумано


class Checklist(BaseModel):
    """
    Основная модель чеклиста (физический, эмоциональный и т.д.)
    """
    __tablename__ = "checklists"
    
    title = Column(String(500), nullable=False)  # "Физический портрет персонажа"
    description = Column(Text)  # Описание чеклиста
    slug = Column(String(100), unique=True, nullable=False)  # "physical-portrait"
    icon = Column(String(50))  # "🎭" или иконка
    order_index = Column(Integer, default=0)  # Порядок отображения
    is_active = Column(Boolean, default=True)
    
    # Новые поля для текстовых блоков
    goal = Column(Text)  # Цель чеклиста
    
    # Relationships
    sections = relationship("ChecklistSection", back_populates="checklist", cascade="all, delete-orphan")


class ChecklistSection(BaseModel):
    """
    Секция чеклиста (тема)
    Например: "1. ВНЕШНОСТЬ И ФИЗИЧЕСКИЕ ДАННЫЕ"
    """
    __tablename__ = "checklist_sections"
    
    checklist_id = Column(Integer, ForeignKey("checklists.id"), nullable=False)
    
    title = Column(String(500), nullable=False)  # "ВНЕШНОСТЬ И ФИЗИЧЕСКИЕ ДАННЫЕ"
    number = Column(String(10))  # "1"
    icon = Column(String(50))  # "📏"
    order_index = Column(Integer, default=0)
    
    # Relationships
    checklist = relationship("Checklist", back_populates="sections")
    subsections = relationship("ChecklistSubsection", back_populates="section", cascade="all, delete-orphan")


class ChecklistSubsection(BaseModel):
    """
    Подсекция чеклиста (раздел темы)
    Например: "1.1 Телосложение и антропометрия"
    """
    __tablename__ = "checklist_subsections"
    
    section_id = Column(Integer, ForeignKey("checklist_sections.id"), nullable=False)
    
    title = Column(String(500), nullable=False)  # "Телосложение и антропометрия"
    number = Column(String(20))  # "1.1"
    order_index = Column(Integer, default=0)
    
    # Новые поля для текстовых блоков
    examples = Column(Text)  # Примеры из литературы
    why_important = Column(Text)  # Почему это важно
    
    # Relationships
    section = relationship("ChecklistSection", back_populates="subsections")
    question_groups = relationship("ChecklistQuestionGroup", back_populates="subsection", cascade="all, delete-orphan")


class ChecklistQuestionGroup(BaseModel):
    """
    Группа вопросов в подсекции
    Например: "Рост и пропорции тела"
    """
    __tablename__ = "checklist_question_groups"
    
    subsection_id = Column(Integer, ForeignKey("checklist_subsections.id"), nullable=False)
    
    title = Column(String(500), nullable=False)  # "Рост и пропорции тела"
    order_index = Column(Integer, default=0)
    
    # Relationships
    subsection = relationship("ChecklistSubsection", back_populates="question_groups")
    questions = relationship("ChecklistQuestion", back_populates="question_group", cascade="all, delete-orphan")


class ChecklistQuestion(BaseModel):
    """
    Отдельный вопрос в группе
    """
    __tablename__ = "checklist_questions"
    
    question_group_id = Column(Integer, ForeignKey("checklist_question_groups.id"), nullable=False)
    
    text = Column(Text, nullable=False)  # Текст вопроса
    hint = Column(Text)  # Подсказка к вопросу
    order_index = Column(Integer, default=0)
    
    # Новые поля для вариантов ответов
    options = Column(JSON)  # Список вариантов ответов
    option_type = Column(String(20), default="none")  # "single", "multiple", "none"
    
    # Новое поле для источников ответа из JSON
    source = Column(JSON)  # Список источников: ["text", "logic", "imagination"]
    
    # Relationships
    question_group = relationship("ChecklistQuestionGroup", back_populates="questions")
    responses = relationship("ChecklistResponse", back_populates="question", cascade="all, delete-orphan")


class ChecklistResponse(BaseModel):
    """
    Ответ пользователя на вопрос чеклиста
    """
    __tablename__ = "checklist_responses"
    
    question_id = Column(Integer, ForeignKey("checklist_questions.id"), nullable=False)
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=False)
    
    # Основной ответ
    answer = Column(Text)  # Текст ответа пользователя
    source_type = Column(Enum(SourceType))  # Тип источника ответа
    comment = Column(Text)  # Комментарий (цитата, обоснование и т.д.)
    
    # Метаданные
    is_current = Column(Boolean, default=True)  # Является ли текущей версией
    version = Column(Integer, default=1)  # Номер версии ответа
    
    # Relationships
    question = relationship("ChecklistQuestion", back_populates="responses")
    character = relationship("Character", back_populates="checklist_responses")


class ChecklistResponseHistory(BaseModel):
    """
    История изменений ответов (версионирование)
    """
    __tablename__ = "checklist_response_history"
    
    response_id = Column(Integer, ForeignKey("checklist_responses.id"), nullable=False)
    
    # Предыдущие значения
    previous_answer = Column(Text)
    previous_source_type = Column(Enum(SourceType))
    previous_comment = Column(Text)
    previous_version = Column(Integer)
    
    # Метаданные изменения
    change_reason = Column(String(200))  # Причина изменения
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    response = relationship("ChecklistResponse")
