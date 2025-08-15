"""
API endpoints для работы с чеклистами
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.dependencies.auth import get_db, get_current_active_user
from app.database.crud import character as character_crud
from app.database.models.user import User
from app.schemas.checklist import (
    Checklist, ChecklistWithResponses, ChecklistStats,
    ChecklistResponse, ChecklistResponseCreate, ChecklistResponseUpdate,
    ChecklistResponseHistory, RestoreResponseVersion
)
from app.services.checklist_service import checklist_service
from app.services.auto_import_service import auto_import_service


router = APIRouter()


@router.get("/", response_model=List[Checklist])
async def get_checklists(
    character_id: Optional[int] = Query(None, description="ID персонажа для получения статистики"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Получение списка доступных чеклистов.
    
    Возвращает все активные чеклисты. Если указан character_id,
    добавляет статистику заполнения для каждого чеклиста.
    """
    # Если указан character_id, проверяем права доступа к персонажу
    if character_id:
        character = character_crud.get(db, id=character_id)
        if not character:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Персонаж не найден"
            )
        
        # Проверяем, что персонаж принадлежит пользователю через текст
        from app.database.crud import text as text_crud
        text = text_crud.get_user_text(db, text_id=character.text_id, user_id=current_user.id)
        if not text:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Нет прав доступа к этому персонажу"
            )
    
    return checklist_service.get_available_checklists(db, character_id)


@router.get("/{checklist_slug}", response_model=ChecklistWithResponses)
async def get_checklist_structure(
    checklist_slug: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Получение структуры чеклиста без привязки к персонажу.
    
    Возвращает полную структуру чеклиста с пустыми ответами.
    """
    checklist = checklist_service.get_checklist_structure(db, checklist_slug)
    
    if not checklist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Чеклист не найден"
        )
    
    return checklist


@router.get("/{checklist_slug}/character/{character_id}", response_model=ChecklistWithResponses)
async def get_checklist_for_character(
    checklist_slug: str,
    character_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Получение чеклиста с ответами конкретного персонажа.
    
    Требует авторизации и проверяет права доступа к персонажу.
    """
    # Проверяем права доступа к персонажу
    character = character_crud.get(db, id=character_id)
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Персонаж не найден"
        )
    
    # Проверяем, что персонаж принадлежит пользователю через текст
    from app.database.crud import text as text_crud
    text = text_crud.get_user_text(db, text_id=character.text_id, user_id=current_user.id)
    if not text:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет прав доступа к этому персонажу"
        )
    
    # Получаем чеклист с ответами
    checklist_with_responses = checklist_service.get_checklist_with_responses(
        db, checklist_slug, character_id
    )
    
    if not checklist_with_responses:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Чеклист не найден"
        )
    
    return checklist_with_responses


class MultipleResponsesRequest(BaseModel):
    question_id: int
    character_id: int
    selected_answer_ids: List[int]
    comment: Optional[str] = None
    source_type: Optional[str] = "FOUND_IN_TEXT"

@router.post("/responses/multiple")
async def manage_multiple_responses(
    request: MultipleResponsesRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Управление множественными ответами на вопрос.
    
    Синхронизирует состояние ответов: добавляет новые, удаляет снятые.
    """
    question_id = request.question_id
    character_id = request.character_id
    selected_answer_ids = request.selected_answer_ids
    comment = request.comment
    source_type = request.source_type
    # Проверяем права доступа к персонажу
    character = character_crud.get(db, id=character_id)
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Персонаж не найден"
        )
    
    from app.database.crud import text as text_crud
    text = text_crud.get_user_text(db, text_id=character.text_id, user_id=current_user.id)
    if not text:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет прав доступа к этому персонажу"
        )
    
    # Получаем текущие ответы
    current_responses = checklist_service.get_current_responses_for_question(db, character_id, question_id)
    current_answer_ids = [r.answer_id for r in current_responses if r.answer_id]
    
    # Определяем изменения
    to_add = [aid for aid in selected_answer_ids if aid not in current_answer_ids]
    to_remove = [aid for aid in current_answer_ids if aid not in selected_answer_ids]
    
    # Добавляем новые ответы
    for answer_id in to_add:
        response_data = ChecklistResponseUpdate(
            answer_id=answer_id,
            comment=comment,
            source_type=source_type,
            answer_text=None  # Убираем обработку кастомного текста
        )
        checklist_service.update_response(db, character_id, question_id, response_data)
    
    # Удаляем снятые ответы
    for answer_id in to_remove:
        # Используем алиас _delete вместо delete_flag
        response_data = ChecklistResponseUpdate(
            answer_id=answer_id,
            **{"_delete": True}  # Используем алиас из схемы
        )
        result = checklist_service.update_response(db, character_id, question_id, response_data)
    
    return {"message": "Ответы успешно обновлены", "added": len(to_add), "removed": len(to_remove)}




@router.post("/responses", response_model=ChecklistResponse)
async def create_or_update_response(
    response_data: ChecklistResponseCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Создание или обновление ответа на вопрос чеклиста.
    
    Автоматически создает новый ответ или обновляет существующий с версионированием.
    """
    # Логирование для отладки
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Received response data: {response_data.dict()}")
        logger.info(f"Character ID: {response_data.character_id}, Question ID: {response_data.question_id}")
    except Exception as e:
        logger.error(f"Error serializing response data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Ошибка валидации данных: {str(e)}"
        )
    
    # Проверяем права доступа к персонажу
    character = character_crud.get(db, id=response_data.character_id)
    if not character:
        logger.error(f"Character with ID {response_data.character_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Персонаж не найден"
        )
    
    from app.database.crud import text as text_crud
    text = text_crud.get_user_text(db, text_id=character.text_id, user_id=current_user.id)
    if not text:
        logger.error(f"User {current_user.id} has no access to character {response_data.character_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет прав доступа к этому персонажу"
        )
    
    # Проверяем существование вопроса
    from app.database.crud.crud_checklist import checklist_question
    question = checklist_question.get(db, id=response_data.question_id)
    if not question:
        logger.error(f"Question with ID {response_data.question_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Вопрос не найден"
        )
    try:
        # Логирование полученных данных
        logger.info(f"Processing response for character_id={response_data.character_id}, question_id={response_data.question_id}")
        logger.info(f"Answer data: answer_id={response_data.answer_id}, answer_text='{response_data.answer_text}', source_type={response_data.source_type}")
        
        # Валидация данных
        if response_data.answer_id is None and not response_data.answer_text:
            logger.error("Both answer_id and answer_text are empty")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Необходимо указать либо answer_id, либо answer_text"
            )
        
        # Если указан answer_id, проверяем его существование
        if response_data.answer_id is not None:
            from app.database.crud.crud_checklist import checklist_answer
            answer = checklist_answer.get(db, id=response_data.answer_id)
            if not answer:
                logger.error(f"Answer with ID {response_data.answer_id} not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Ответ не найден"
                )
            # Проверяем, что ответ принадлежит указанному вопросу
            if answer.question_id != response_data.question_id:
                logger.error(f"Answer {response_data.answer_id} does not belong to question {response_data.question_id}")
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Ответ не принадлежит указанному вопросу"
                )
        
        # Преобразуем в ChecklistResponseUpdate для единообразия
        update_data = ChecklistResponseUpdate(
            answer_id=response_data.answer_id,
            answer_text=response_data.answer_text,
            comment=response_data.comment,
            source_type=response_data.source_type
        )
        
        logger.info(f"Calling checklist_service.update_response with validated data")
        response = checklist_service.update_response(
            db, response_data.character_id, response_data.question_id, update_data
        )
        
        logger.info(f"Successfully created/updated response with id={response.id}")
        return response
        
    except HTTPException:
        # Перебрасываем HTTPException как есть
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating/updating response: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )


@router.delete("/responses/{response_id}")
async def delete_response(
    response_id: int,
    delete_reason: Optional[str] = Query(None, description="Причина удаления"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Удаление ответа с подтверждением.
    
    Сохраняет удаленный ответ в историю для возможного восстановления.
    """
    # Проверяем права доступа
    from app.database.crud.crud_checklist_response import checklist_response
    response = checklist_response.get(db, id=response_id)
    
    if not response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ответ не найден"
        )
    
    character = character_crud.get(db, id=response.character_id)
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Персонаж не найден"
        )
    
    from app.database.crud import text as text_crud
    text = text_crud.get_user_text(db, text_id=character.text_id, user_id=current_user.id)
    if not text:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет прав доступа к этому ответу"
        )
    
    success = checklist_service.delete_response(
        db, response_id, delete_reason or "Удаление пользователем"
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Не удалось удалить ответ"
        )
    
    return {"message": "Ответ успешно удален"}


@router.get("/character/{character_id}/progress", response_model=List[ChecklistStats])
async def get_character_progress(
    character_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Получение прогресса заполнения всех чеклистов для персонажа.
    
    Возвращает статистику по всем доступным чеклистам.
    """
    # Проверяем права доступа к персонажу
    character = character_crud.get(db, id=character_id)
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Персонаж не найден"
        )
    
    from app.database.crud import text as text_crud
    text = text_crud.get_user_text(db, text_id=character.text_id, user_id=current_user.id)
    if not text:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет прав доступа к этому персонажу"
        )
    
    progress = checklist_service.get_character_progress(db, character_id)
    return progress


@router.post("/import")
async def import_checklists_manually(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Ручной импорт чеклистов из файла checklists_to_import.txt.
    
    Импортирует все чеклисты, указанные в конфигурационном файле.
    Доступно только авторизованным пользователям.
    """
    try:
        result = await auto_import_service.manual_import_checklists()
        
        if result["success"]:
            return {
                "message": result["message"],
                "imported": result["imported"],
                "skipped": result["skipped"],
                "errors": result["errors"]
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при импорте чеклистов: {str(e)}"
        )


@router.get("/import/status")
async def get_import_status(
    current_user: User = Depends(get_current_active_user)
):
    """
    Получение информации о доступных для импорта чеклистах.
    
    Возвращает список чеклистов из конфигурационного файла.
    """
    try:
        checklists = auto_import_service.load_checklist_list()
        
        return {
            "total_checklists": len(checklists),
            "checklists": [
                {
                    "file_path": file_path
                }
                for file_path in checklists
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении статуса импорта: {str(e)}"
        )
