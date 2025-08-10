"""
API endpoints для управления текстами произведений.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.dependencies.auth import get_db, get_current_active_user
from app.database.crud import text as text_crud, project as project_crud
from app.database.models.user import User
from app.schemas.text import Text, TextUpdate, TextWithCharacters
from app.services.nlp_processor import get_nlp_processor
from app.services.nlp.models import NLPResult


router = APIRouter()


@router.get("/{text_id}", response_model=Text)
async def get_text(
    text_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Получение текста по ID.
    
    Требует авторизации. Пользователь может получить только тексты своих проектов.
    """
    # Получаем текст с проверкой прав доступа
    text = text_crud.get_user_text(db, text_id=text_id, user_id=current_user.id)
    
    if not text:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Текст не найден или нет прав доступа"
        )
    
    return text


@router.put("/{text_id}", response_model=Text)
async def update_text(
    text_id: int,
    text_update: TextUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Обновление метаданных текста.
    
    - **filename**: Новое имя файла (опционально)
    - **file_metadata**: Новые метаданные файла (опционально)
    - **processed_at**: Метка времени обработки (опционально)
    
    Требует авторизации. Пользователь может обновлять только тексты своих проектов.
    """
    # Получаем текст с проверкой прав доступа
    text = text_crud.get_user_text(db, text_id=text_id, user_id=current_user.id)
    
    if not text:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Текст не найден или нет прав доступа"
        )
    
    try:
        updated_text = text_crud.update(db, db_obj=text, obj_in=text_update)
        return updated_text
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обновлении текста: {str(e)}"
        )


@router.delete("/{text_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_text(
    text_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Удаление текста.
    
    Требует авторизации. Пользователь может удалять только тексты своих проектов.
    
    ВНИМАНИЕ: Это действие необратимо. Все персонажи этого текста также будут удалены.
    """
    # Получаем текст с проверкой прав доступа
    text = text_crud.get_user_text(db, text_id=text_id, user_id=current_user.id)
    
    if not text:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Текст не найден или нет прав доступа"
        )
    
    try:
        text_crud.remove(db, id=text_id)
        # Возвращаем 204 No Content при успешном удалении
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при удалении текста: {str(e)}"
        )


@router.get("/{text_id}/characters", response_model=List[dict])
async def get_text_characters(
    text_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Получение персонажей из текста.
    
    Требует авторизации. Пользователь может видеть персонажей только из текстов своих проектов.
    """
    # Сначала проверяем права доступа к тексту
    text = text_crud.get_user_text(db, text_id=text_id, user_id=current_user.id)
    
    if not text:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Текст не найден или нет прав доступа"
        )
    
    # Получаем персонажей через связанные объекты
    return [
        {
            "id": character.id,
            "name": character.name,
            "aliases": character.aliases,
            "importance_score": character.importance_score,
            "speech_attribution": character.speech_attribution,
            "created_at": character.created_at.isoformat() if character.created_at else None
        }
        for character in text.characters
    ]


@router.post("/{text_id}/process")
async def mark_text_as_processed(
    text_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Отметить текст как обработанный (без NLP анализа).
    
    Требует авторизации. Пользователь может обрабатывать только тексты своих проектов.
    
    Возвращает статус обработки.
    """
    # Проверяем права доступа к тексту
    text = text_crud.get_user_text(db, text_id=text_id, user_id=current_user.id)
    
    if not text:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Текст не найден или нет прав доступа"
        )
    
    # Проверяем, что у текста есть содержимое для обработки
    if not text.content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Текст не содержит данных для обработки"
        )
    
    # Проверяем, не обработан ли уже текст
    if text.processed_at:
        return {
            "message": "Текст уже обработан",
            "processed_at": text.processed_at.isoformat(),
            "status": "already_processed"
        }
    
    try:
        # Отмечаем текст как обработанный
        # В будущем здесь будет вызов NLP модуля
        processed_text = text_crud.mark_as_processed(db, text_id=text_id)
        
        return {
            "message": "Текст отмечен как обработанный",
            "text_id": text_id,
            "status": "marked_as_processed",
            "processed_at": processed_text.processed_at.isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при запуске обработки текста: {str(e)}"
        )


@router.get("/{text_id}/statistics")
async def get_text_statistics(
    text_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Получение статистики текста.
    
    Возвращает количество персонажей, статус обработки и другую аналитику.
    
    Требует авторизации. Пользователь может видеть статистику только своих текстов.
    """
    # Проверяем права доступа к тексту
    text = text_crud.get_user_text(db, text_id=text_id, user_id=current_user.id)
    
    if not text:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Текст не найден или нет прав доступа"
        )
    
    # Собираем статистику
    characters_count = len(text.characters)
    content_length = len(text.content) if text.content else 0
    
    return {
        "text_id": text_id,
        "filename": text.filename,
        "original_format": text.original_format,
        "characters_count": characters_count,
        "content_length": content_length,
        "is_processed": text.processed_at is not None,
        "processed_at": text.processed_at.isoformat() if text.processed_at else None,
        "created_at": text.created_at.isoformat(),
        "updated_at": text.updated_at.isoformat()
    }


@router.get("/{text_id}/content")
async def get_text_content(
    text_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Получение содержимого текста.
    
    Требует авторизации. Пользователь может читать содержимое только своих текстов.
    
    Возвращает полное содержимое текста.
    """
    # Проверяем права доступа к тексту
    text = text_crud.get_user_text(db, text_id=text_id, user_id=current_user.id)
    
    if not text:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Текст не найден или нет прав доступа"
        )
    
    if not text.content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Содержимое текста отсутствует"
        )
    
    return {
        "text_id": text_id,
        "filename": text.filename,
        "content": text.content,
        "content_length": len(text.content),
        "original_format": text.original_format
    }


@router.post("/{text_id}/process", response_model=NLPResult)
async def process_text(
    text_id: int,
    force_reprocess: bool = False,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Обработка текста через NLP модуль.
    
    Извлекает персонажей, анализирует их речь и сохраняет результаты в БД.
    Требует авторизации. Пользователь может обрабатывать только свои тексты.
    
    Args:
        text_id: ID текста для обработки
        force_reprocess: Принудительная переобработка (игнорировать кэш)
    
    Returns:
        Результат NLP анализа с персонажами и статистикой
    """
    try:
        # Проверяем права доступа к тексту
        text = text_crud.get_user_text(db, text_id=text_id, user_id=current_user.id)
        
        if not text:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Текст не найден или нет прав доступа"
            )
        
        if not text.content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Содержимое текста отсутствует. Загрузите текст сначала."
            )
        
        # Получаем NLP процессор и обрабатываем текст
        nlp_processor = get_nlp_processor()
        result = await nlp_processor.process_text(
            text_id=text_id,
            db=db,
            force_reprocess=force_reprocess
        )
        
        return result
        
    except ValueError as e:
        # Ошибки валидации (например, текст не найден)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Неожиданные ошибки
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обработке текста: {str(e)}"
        )
