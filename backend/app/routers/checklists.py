"""
API endpoints для работы с чеклистами
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session

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
    # Проверяем права доступа к персонажу
    character = character_crud.get(db, id=response_data.character_id)
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
    
    try:
        # Преобразуем в ChecklistResponseUpdate для единообразия
        update_data = ChecklistResponseUpdate(
            answer_id=response_data.answer_id,
            comment=response_data.comment,
            source_type=response_data.source_type
        )
        
        response = checklist_service.update_response(
            db, response_data.character_id, response_data.question_id, update_data
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка при сохранении ответа: {str(e)}"
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
