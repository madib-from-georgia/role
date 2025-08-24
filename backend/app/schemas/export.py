"""
Pydantic схемы для экспорта данных.
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class ExportFormat(str, Enum):
    """Поддерживаемые форматы экспорта."""
    PDF = "pdf"
    DOCX = "docx"


class ReportType(str, Enum):
    """Типы отчетов для экспорта."""
    QUESTIONNAIRE_EMPTY = "questionnaire_empty"  # Опросник без ответов
    QUESTIONNAIRE_WITH_ANSWERS = "questionnaire_with_answers"  # Опросник с ответами
    QUESTIONNAIRE_FULL = "questionnaire_full"  # Опросник с ответами, советами и упражнениями
    ANSWERS_ONLY = "answers_only"  # Только список ответов пользователя


class ExportRequest(BaseModel):
    """Запрос на экспорт данных персонажа."""
    character_id: int = Field(..., description="ID персонажа для экспорта")
    format: ExportFormat = Field(..., description="Формат экспорта")
    report_type: ReportType = Field(default=ReportType.QUESTIONNAIRE_WITH_ANSWERS, description="Тип отчета")
    include_checklists: Optional[List[str]] = Field(
        default=None,
        description="Список slug'ов чеклистов для включения (если None - все)"
    )
    include_empty_responses: bool = Field(
        default=False,
        description="Включать ли вопросы без ответов"
    )


class ExportResponse(BaseModel):
    """Ответ с информацией об экспорте."""
    filename: str = Field(..., description="Имя файла")
    content_type: str = Field(..., description="MIME тип файла")
    size_bytes: int = Field(..., description="Размер файла в байтах")
    export_date: str = Field(..., description="Дата и время экспорта")


class ExportStatus(BaseModel):
    """Статус экспорта для асинхронных операций."""
    status: str = Field(..., description="Статус: processing, completed, failed")
    progress: Optional[float] = Field(None, description="Прогресс (0.0 - 1.0)")
    message: Optional[str] = Field(None, description="Сообщение о статусе")
    download_url: Optional[str] = Field(None, description="URL для скачивания готового файла")


class ExportTemplateInfo(BaseModel):
    """Информация о доступном шаблоне экспорта."""
    name: str = Field(..., description="Название шаблона")
    description: str = Field(..., description="Описание шаблона")
    supported_formats: List[ExportFormat] = Field(..., description="Поддерживаемые форматы")
    supports_customization: bool = Field(default=False, description="Поддерживает ли настройку")


class BulkExportRequest(BaseModel):
    """Запрос на массовый экспорт нескольких персонажей."""
    character_ids: List[int] = Field(..., description="Список ID персонажей")
    format: ExportFormat = Field(..., description="Формат экспорта")
    report_type: ReportType = Field(default=ReportType.QUESTIONNAIRE_WITH_ANSWERS, description="Тип отчета")
    merge_into_single_file: bool = Field(
        default=True,
        description="Объединять ли всех персонажей в один файл"
    )


class ExportCustomization(BaseModel):
    """Настройки для кастомизации экспорта."""
    include_logo: bool = Field(default=True, description="Включать логотип")
    include_metadata: bool = Field(default=True, description="Включать метаданные")
    color_scheme: Optional[str] = Field(default="default", description="Цветовая схема")
    font_size: Optional[int] = Field(default=12, description="Размер шрифта")
    page_orientation: Optional[str] = Field(default="portrait", description="Ориентация страницы")
