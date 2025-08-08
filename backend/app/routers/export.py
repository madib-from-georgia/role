"""
API endpoints для экспорта данных персонажей.
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
from loguru import logger
import io
import time
from datetime import datetime

from app.dependencies.auth import get_db, get_current_active_user
from app.database.crud import character as character_crud
from app.database.models.user import User
from app.schemas.export import (
    ExportRequest, ExportResponse, ExportFormat, ExportType, 
    ExportTemplateInfo, BulkExportRequest
)
from app.services.export_service import export_service
from app.services.checklist_service import checklist_service
from app.utils.error_handlers import (
    character_not_found, access_denied, ExportError, 
    ValidationError, handle_errors
)
from app.utils.logging_config import LoggingConfig


router = APIRouter(prefix="/api/export", tags=["export"])


@router.post("/character", response_class=StreamingResponse)
async def export_character(
    export_request: ExportRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Экспорт данных персонажа в указанном формате.
    
    - **character_id**: ID персонажа для экспорта
    - **format**: Формат файла (pdf, docx)
    - **export_type**: Тип детализации (detailed, summary, compact)
    - **include_checklists**: Список конкретных чеклистов (опционально)
    - **include_empty_responses**: Включать ли пустые ответы
    """
    start_time = time.time()
    
    try:
        # Проверяем доступ к персонажу
        character = character_crud.get(db, id=export_request.character_id)
        if not character:
            raise character_not_found(export_request.character_id)
        
        # Загружаем связанные данные для проверки доступа
        from app.database.crud import text as text_crud
        text = text_crud.get_user_text(db, text_id=character.text_id, user_id=current_user.id)
        if not text:
            raise access_denied("персонажу")
        
        # Получаем данные чеклистов персонажа
        if export_request.include_checklists:
            # Фильтруем по указанным чеклистам
            checklists = []
            for checklist_slug in export_request.include_checklists:
                checklist_data = checklist_service.get_checklist_with_responses(
                    db, checklist_slug, export_request.character_id
                )
                if checklist_data:
                    checklists.append(checklist_data)
        else:
            # Получаем все доступные чеклисты и фильтруем с ответами
            all_checklists = checklist_service.get_available_checklists(db)
            checklists = []
            for checklist in all_checklists:
                checklist_data = checklist_service.get_checklist_with_responses(
                    db, checklist.slug, export_request.character_id
                )
                if checklist_data:
                    checklists.append(checklist_data)
        
        # Фильтруем пустые ответы если нужно (ChecklistWithResponses имеет структуру sections)
        if not export_request.include_empty_responses:
            # Для ChecklistWithResponses фильтрация не нужна, так как в get_checklist_with_responses
            # уже возвращаются только вопросы с current_response
            pass
        
        # Генерируем файл в зависимости от формата
        if export_request.format == ExportFormat.PDF:
            file_content = await export_service.export_character_pdf(
                character, checklists, export_request.export_type, current_user.id
            )
            content_type = "application/pdf"
            file_extension = "pdf"
        elif export_request.format == ExportFormat.DOCX:
            file_content = await export_service.export_character_docx(
                character, checklists, export_request.export_type, current_user.id
            )
            content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            file_extension = "docx"
        else:
            raise ValidationError(f"Неподдерживаемый формат: {export_request.format}")
        
        # Формируем имя файла
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        character_name_safe = "".join(c for c in character.name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"character_{character_name_safe}_{timestamp}.{file_extension}"
        
        # Логируем успешный экспорт
        duration_ms = (time.time() - start_time) * 1000
        LoggingConfig.log_api_request(
            method="POST",
            url="/api/export/character",
            user_id=current_user.id,
            duration_ms=duration_ms,
            status_code=200,
            character_id=export_request.character_id,
            format=export_request.format,
            export_type=export_request.export_type
        )
        
        # Возвращаем файл с правильным кодированием имени
        from urllib.parse import quote
        encoded_filename = quote(filename.encode('utf-8'))
        return StreamingResponse(
            io.BytesIO(file_content),
            media_type=content_type,
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
            }
        )
        
    except (ValidationError, ExportError) as e:
        # Логируем ошибку приложения
        duration_ms = (time.time() - start_time) * 1000
        LoggingConfig.log_api_request(
            method="POST",
            url="/api/export/character",
            user_id=current_user.id,
            duration_ms=duration_ms,
            status_code=e.http_status,
            error=str(e)
        )
        raise HTTPException(status_code=e.http_status, detail=e.message)
        
    except Exception as e:
        # Логируем неожиданную ошибку с полным трейсом
        import traceback
        error_trace = traceback.format_exc()
        
        duration_ms = (time.time() - start_time) * 1000
        LoggingConfig.log_api_request(
            method="POST",
            url="/api/export/character",
            user_id=current_user.id,
            duration_ms=duration_ms,
            status_code=500,
            error=f"{str(e)}\n{error_trace}"
        )
        
        # В режиме разработки показываем подробную ошибку
        logger.error(f"Export error: {str(e)}")
        logger.error(f"Traceback: {error_trace}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка экспорта: {str(e)}"
        )


@router.post("/characters/bulk", response_class=StreamingResponse)
async def export_characters_bulk(
    bulk_request: BulkExportRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Массовый экспорт нескольких персонажей.
    
    - **character_ids**: Список ID персонажей
    - **format**: Формат файла (pdf, docx)
    - **export_type**: Тип детализации
    - **merge_into_single_file**: Объединять ли в один файл
    """
    if not bulk_request.character_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Список персонажей не может быть пустым"
        )
    
    # Проверяем доступ ко всем персонажам
    characters = []
    for char_id in bulk_request.character_ids:
        character = character_crud.get_character_by_id(db, char_id)
        if not character:
            raise character_not_found(char_id)
        
        if character.text.project.user_id != current_user.id:
            raise access_denied(f"персонажу с ID {char_id}")
        
        characters.append(character)
    
    try:
        if bulk_request.merge_into_single_file:
            # Экспортируем все персонажи в один файл
            # TODO: Реализовать объединенный экспорт
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="Объединенный экспорт пока не реализован"
            )
        else:
            # Экспортируем каждого персонажа отдельно и создаем ZIP архив
            # TODO: Реализовать ZIP архив с несколькими файлами
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="ZIP архив для нескольких файлов пока не реализован"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при массовом экспорте: {str(e)}"
        )


@router.get("/templates", response_model=List[ExportTemplateInfo])
async def get_export_templates(
    current_user: User = Depends(get_current_active_user)
):
    """
    Получение списка доступных шаблонов экспорта.
    """
    templates = [
        ExportTemplateInfo(
            name="Стандартный",
            description="Стандартный шаблон с полной информацией о персонаже",
            supported_formats=[ExportFormat.PDF, ExportFormat.DOCX],
            supports_customization=True
        ),
        ExportTemplateInfo(
            name="Краткий",
            description="Краткий обзор с основной статистикой",
            supported_formats=[ExportFormat.PDF, ExportFormat.DOCX],
            supports_customization=False
        ),
        ExportTemplateInfo(
            name="Компактный",
            description="Минимальная информация для быстрого обзора",
            supported_formats=[ExportFormat.PDF, ExportFormat.DOCX],
            supports_customization=False
        )
    ]
    
    return templates


@router.get("/formats", response_model=List[str])
async def get_supported_formats(
    current_user: User = Depends(get_current_active_user)
):
    """
    Получение списка поддерживаемых форматов экспорта.
    """
    return [format_type.value for format_type in ExportFormat]


@router.get("/types", response_model=List[str])
async def get_export_types(
    current_user: User = Depends(get_current_active_user)
):
    """
    Получение списка доступных типов экспорта.
    """
    return [export_type.value for export_type in ExportType]
