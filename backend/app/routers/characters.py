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
async def get_character_checklists(character_id: int, db: Session = Depends(get_db)):
    """Получение всех чеклистов персонажа."""
    return {"message": f"Get checklists for character {character_id} endpoint - в разработке"}


@router.get("/{character_id}/checklists/{checklist_type}")
async def get_character_checklist(
    character_id: int, 
    checklist_type: str, 
    db: Session = Depends(get_db)
):
    """Получение конкретного чеклиста персонажа."""
    return {
        "message": f"Get checklist {checklist_type} for character {character_id} endpoint - в разработке"
    }


@router.post("/{character_id}/checklists/{checklist_type}")
async def save_checklist_responses(
    character_id: int, 
    checklist_type: str, 
    db: Session = Depends(get_db)
):
    """Сохранение ответов чеклиста."""
    return {
        "message": f"Save checklist {checklist_type} for character {character_id} endpoint - в разработке"
    }


@router.put("/{character_id}/checklists/{checklist_type}")
async def update_checklist_responses(
    character_id: int, 
    checklist_type: str, 
    db: Session = Depends(get_db)
):
    """Обновление ответов чеклиста."""
    return {
        "message": f"Update checklist {checklist_type} for character {character_id} endpoint - в разработке"
    }


@router.get("/{character_id}/export/pdf")
async def export_character_pdf(character_id: int, db: Session = Depends(get_db)):
    """Экспорт анализа персонажа в PDF."""
    return {"message": f"Export character {character_id} to PDF endpoint - в разработке"}


@router.get("/{character_id}/export/docx")
async def export_character_docx(character_id: int, db: Session = Depends(get_db)):
    """Экспорт анализа персонажа в DOCX."""
    return {"message": f"Export character {character_id} to DOCX endpoint - в разработке"}
