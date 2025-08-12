"""
API эндпоинты для управления версиями чеклистов
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from loguru import logger

from app.database.connection import get_db
from app.services.checklist_version_service import checklist_version_service
from app.services.response_migration_service import response_migration_service
from app.schemas.checklist import Checklist
from app.database.crud.crud_checklist import checklist as checklist_crud


router = APIRouter(prefix="/checklist-versions", tags=["checklist-versions"])


@router.post("/{checklist_id}/check-updates")
async def check_for_updates(
    checklist_id: int,
    json_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Проверяет наличие обновлений для чеклиста
    
    Args:
        checklist_id: ID чеклиста
        json_file: Новый JSON файл для проверки
        db: Сессия базы данных
        
    Returns:
        Информация об обновлениях
    """
    try:
        # Читаем содержимое файла
        content = await json_file.read()
        json_content = content.decode('utf-8')
        
        # Проверяем обновления
        update_info = checklist_version_service.check_for_updates(
            db, checklist_id, json_content
        )
        
        return {
            "success": True,
            "data": update_info
        }
        
    except Exception as e:
        logger.error(f"Ошибка проверки обновлений: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{checklist_id}/analyze-changes")
async def analyze_changes(
    checklist_id: int,
    json_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Анализирует изменения между версиями чеклиста
    
    Args:
        checklist_id: ID чеклиста
        json_file: Новый JSON файл
        db: Сессия базы данных
        
    Returns:
        Детальный анализ изменений
    """
    try:
        content = await json_file.read()
        json_content = content.decode('utf-8')
        
        # Анализируем изменения
        changes = checklist_version_service.analyze_changes(
            db, checklist_id, json_content
        )
        
        return {
            "success": True,
            "data": changes
        }
        
    except Exception as e:
        logger.error(f"Ошибка анализа изменений: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{checklist_id}/update")
async def update_checklist_version(
    checklist_id: int,
    json_file: UploadFile = File(...),
    force_update: bool = Form(False),
    migrate_responses: bool = Form(True),
    db: Session = Depends(get_db)
):
    """
    Обновляет чеклист до новой версии
    
    Args:
        checklist_id: ID чеклиста
        json_file: Новый JSON файл
        force_update: Принудительное обновление
        migrate_responses: Мигрировать ответы пользователей
        db: Сессия базы данных
        
    Returns:
        Результат обновления
    """
    try:
        content = await json_file.read()
        json_content = content.decode('utf-8')
        
        # Обновляем чеклист
        result = checklist_version_service.update_checklist(
            db, checklist_id, json_content, force_update, migrate_responses
        )
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Ошибка обновления чеклиста: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{checklist_id}/versions")
async def get_checklist_versions(
    checklist_id: int,
    db: Session = Depends(get_db)
):
    """
    Получает историю версий чеклиста
    
    Args:
        checklist_id: ID чеклиста
        db: Сессия базы данных
        
    Returns:
        История версий
    """
    try:
        versions = checklist_version_service.get_version_history(db, checklist_id)
        
        return {
            "success": True,
            "data": versions
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения версий: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{checklist_id}/migration/analyze")
async def analyze_migration_impact(
    checklist_id: int,
    json_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Анализирует влияние обновления на ответы пользователей
    
    Args:
        checklist_id: ID чеклиста
        json_file: Новый JSON файл
        db: Сессия базы данных
        
    Returns:
        Анализ влияния на ответы пользователей
    """
    try:
        content = await json_file.read()
        json_content = content.decode('utf-8')
        
        # Сначала анализируем изменения
        changes = checklist_version_service.analyze_changes(
            db, checklist_id, json_content
        )
        
        # Затем анализируем влияние на ответы
        impact = response_migration_service.analyze_migration_impact(
            db, checklist_id, changes.get("entity_matches", {})
        )
        
        return {
            "success": True,
            "data": impact
        }
        
    except Exception as e:
        logger.error(f"Ошибка анализа влияния миграции: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{checklist_id}/migration/execute")
async def execute_migration(
    checklist_id: int,
    migration_plan: Dict[str, Any],
    dry_run: bool = Form(False),
    db: Session = Depends(get_db)
):
    """
    Выполняет миграцию ответов пользователей
    
    Args:
        checklist_id: ID чеклиста
        migration_plan: План миграции
        dry_run: Тестовый режим
        db: Сессия базы данных
        
    Returns:
        Результаты миграции
    """
    try:
        results = response_migration_service.execute_migration(
            db, checklist_id, migration_plan, dry_run
        )
        
        return {
            "success": True,
            "data": results
        }
        
    except Exception as e:
        logger.error(f"Ошибка выполнения миграции: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{checklist_id}/migration/report")
async def get_migration_report(
    checklist_id: int,
    db: Session = Depends(get_db)
):
    """
    Получает отчет о последней миграции
    
    Args:
        checklist_id: ID чеклиста
        db: Сессия базы данных
        
    Returns:
        Отчет о миграции
    """
    try:
        # Получаем последний анализ влияния (в реальном приложении это должно храниться)
        # Пока возвращаем базовую информацию
        checklist_obj = checklist_crud.get(db, id=checklist_id)
        if not checklist_obj:
            raise HTTPException(status_code=404, detail="Чеклист не найден")
        
        report = {
            "checklist_id": checklist_id,
            "checklist_title": checklist_obj.title,
            "current_version": checklist_obj.version,
            "file_hash": checklist_obj.file_hash,
            "last_updated": checklist_obj.updated_at.isoformat() if checklist_obj.updated_at else None
        }
        
        return {
            "success": True,
            "data": report
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения отчета: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{character_id}/migration-tasks")
async def get_user_migration_tasks(
    character_id: int,
    checklist_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Получает задачи миграции для пользователя
    
    Args:
        character_id: ID персонажа
        checklist_id: ID чеклиста (опционально)
        db: Сессия базы данных
        
    Returns:
        Список задач для пользователя
    """
    try:
        if checklist_id:
            tasks = response_migration_service.get_user_migration_tasks(
                db, character_id, checklist_id
            )
        else:
            # Получаем задачи по всем чеклистам
            tasks = []
            # В реальном приложении здесь был бы запрос ко всем чеклистам пользователя
        
        return {
            "success": True,
            "data": tasks
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения задач пользователя: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/user/response/{response_id}/restore")
async def restore_user_response(
    response_id: int,
    new_answer_id: Optional[int] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Восстанавливает архивированный ответ пользователя
    
    Args:
        response_id: ID ответа
        new_answer_id: ID нового ответа (если изменился)
        db: Сессия базы данных
        
    Returns:
        Результат восстановления
    """
    try:
        success = response_migration_service.restore_response(
            db, response_id, new_answer_id
        )
        
        if success:
            return {
                "success": True,
                "message": "Ответ успешно восстановлен"
            }
        else:
            raise HTTPException(status_code=400, detail="Не удалось восстановить ответ")
        
    except Exception as e:
        logger.error(f"Ошибка восстановления ответа: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{checklist_id}/compatibility/{target_checklist_id}")
async def check_compatibility(
    checklist_id: int,
    target_checklist_id: int,
    db: Session = Depends(get_db)
):
    """
    Проверяет совместимость между двумя версиями чеклиста
    
    Args:
        checklist_id: ID исходного чеклиста
        target_checklist_id: ID целевого чеклиста
        db: Сессия базы данных
        
    Returns:
        Информация о совместимости
    """
    try:
        # Получаем чеклисты
        source_checklist = checklist_crud.get(db, id=checklist_id)
        target_checklist = checklist_crud.get(db, id=target_checklist_id)
        
        if not source_checklist or not target_checklist:
            raise HTTPException(status_code=404, detail="Один из чеклистов не найден")
        
        # Проверяем совместимость по external_id
        compatibility = {
            "compatible": source_checklist.external_id == target_checklist.external_id,
            "source_version": source_checklist.version,
            "target_version": target_checklist.version,
            "source_hash": source_checklist.file_hash,
            "target_hash": target_checklist.file_hash,
            "same_structure": source_checklist.external_id == target_checklist.external_id
        }
        
        return {
            "success": True,
            "data": compatibility
        }
        
    except Exception as e:
        logger.error(f"Ошибка проверки совместимости: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{checklist_id}/rollback/{target_version}")
async def rollback_checklist(
    checklist_id: int,
    target_version: str,
    db: Session = Depends(get_db)
):
    """
    Откатывает чеклист к предыдущей версии
    
    Args:
        checklist_id: ID чеклиста
        target_version: Целевая версия для отката
        db: Сессия базы данных
        
    Returns:
        Результат отката
    """
    try:
        # В реальном приложении здесь была бы логика отката
        # Пока возвращаем заглушку
        return {
            "success": False,
            "message": "Функция отката пока не реализована"
        }
        
    except Exception as e:
        logger.error(f"Ошибка отката: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))