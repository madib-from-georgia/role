"""
Роутер для управления персонажами.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.dependencies.auth import get_db, get_current_active_user
from app.database.crud import character as character_crud, text as text_crud
from app.database.models.user import User
from app.schemas.character import Character, CharacterUpdate
from app.schemas.checklist import ChecklistResponseCreate, ChecklistResponseUpdate

router = APIRouter()


@router.get("/{character_id}", response_model=Character)
async def get_character(
    character_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Получение данных персонажа.
    
    Требует авторизации. Пользователь может видеть персонажей только из своих проектов.
    """
    try:
        # Получаем персонажа
        character = character_crud.get(db, id=character_id)
        
        if not character:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Персонаж не найден"
            )
        
        # Проверяем права доступа через текст
        text = text_crud.get_user_text(db, text_id=character.text_id, user_id=current_user.id)
        
        if not text:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Персонаж не найден или нет прав доступа"
            )
        
        return character
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении персонажа: {str(e)}"
        )


@router.put("/{character_id}", response_model=Character)
async def update_character(
    character_id: int,
    character_update: CharacterUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Обновление данных персонажа.
    
    Требует авторизации. Пользователь может обновлять персонажей только из своих проектов.
    """
    try:
        # Получаем персонажа
        character = character_crud.get(db, id=character_id)
        
        if not character:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Персонаж не найден"
            )
        
        # Проверяем права доступа через текст
        text = text_crud.get_user_text(db, text_id=character.text_id, user_id=current_user.id)
        
        if not text:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Персонаж не найден или нет прав доступа"
            )
        
        # Обновляем персонажа
        updated_character = character_crud.update(db, db_obj=character, obj_in=character_update)
        
        return updated_character
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обновлении персонажа: {str(e)}"
        )


@router.get("/{character_id}/checklists")
async def get_character_checklists(
    character_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Получение всех чеклистов персонажа."""
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
    
    from app.services.checklist_service import checklist_service
    return checklist_service.get_character_progress(db, character_id)


@router.get("/{character_id}/checklists/{checklist_type}")
async def get_character_checklist(
    character_id: int, 
    checklist_type: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Получение конкретного чеклиста персонажа."""
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
    
    from app.services.checklist_service import checklist_service
    checklist_with_responses = checklist_service.get_checklist_with_responses(
        db, checklist_type, character_id
    )
    
    if not checklist_with_responses:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Чеклист не найден"
        )
    
    return checklist_with_responses


@router.post("/{character_id}/checklists/{checklist_type}")
async def save_checklist_responses(
    character_id: int, 
    checklist_type: str,
    response_data: ChecklistResponseCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Сохранение ответов чеклиста."""
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
    
    # Проверяем соответствие character_id в URL и данных
    if response_data.character_id != character_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID персонажа в URL не соответствует данным запроса"
        )
    
    try:
        from app.services.checklist_service import checklist_service
        # Преобразуем в ChecklistResponseUpdate для единообразия
        from app.schemas.checklist import ChecklistResponseUpdate
        update_data = ChecklistResponseUpdate(
            answer=response_data.answer,
            source_type=response_data.source_type,
            comment=response_data.comment
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


@router.put("/{character_id}/checklists/{checklist_type}")
async def update_checklist_responses(
    character_id: int, 
    checklist_type: str,
    response_data: ChecklistResponseUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Обновление ответов чеклиста."""
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
    
    try:
        from app.services.checklist_service import checklist_service
        # Для PUT запроса нужно указать question_id из тела запроса
        if not hasattr(response_data, 'question_id') or not response_data.question_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Для обновления ответа необходимо указать question_id"
            )
        
        response = checklist_service.update_response(
            db, character_id, response_data.question_id, response_data
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка при обновлении ответа: {str(e)}"
        )


@router.get("/{character_id}/export/pdf")
async def export_character_pdf(character_id: int, db: Session = Depends(get_db)):
    """Экспорт анализа персонажа в PDF."""
    return {"message": f"Export character {character_id} to PDF endpoint - в разработке"}


@router.get("/{character_id}/export/docx")
async def export_character_docx(character_id: int, db: Session = Depends(get_db)):
    """Экспорт анализа персонажа в DOCX."""
    return {"message": f"Export character {character_id} to DOCX endpoint - в разработке"}
