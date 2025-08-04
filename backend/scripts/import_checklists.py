"""
Скрипт для импорта чеклистов из Markdown файлов в базу данных
"""

import asyncio
import sys
from pathlib import Path

# Добавляем корневую директорию в Python path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.database.connection import SessionLocal, init_db
from app.services.checklist_service import checklist_service
from loguru import logger


CHECKLIST_FILES = [
    ("docs/modules/01-physical-portrait/ACTOR_PHYSICAL_CHECKLIST.md", "Физический портрет персонажа"),
    ("docs/modules/02-emotional-profile/ACTOR_EMOTIONAL_CHECKLIST.md", "Эмоциональный профиль персонажа")
]


async def import_checklist_files():
    """Импорт чеклистов из файлов"""
    
    # Инициализируем базу данных
    await init_db()
    
    db: Session = SessionLocal()
    
    try:
        for file_path, description in CHECKLIST_FILES:
            full_path = Path(__file__).parent.parent.parent / file_path
            
            if not full_path.exists():
                logger.warning(f"Файл не найден: {full_path}")
                continue
            
            try:
                logger.info(f"Импорт чеклиста: {description}")
                
                # Сначала валидируем файл
                validation = checklist_service.validate_checklist_file(str(full_path))
                
                if not validation["valid"]:
                    logger.error(f"Файл не прошел валидацию: {validation['errors']}")
                    continue
                
                logger.info(f"Структура файла: {validation['summary']}")
                
                # Импортируем в базу данных
                checklist = checklist_service.import_checklist_from_file(db, str(full_path))
                
                logger.success(f"Чеклист '{checklist.title}' успешно импортирован (ID: {checklist.id})")
                
            except ValueError as e:
                logger.warning(f"Чеклист уже существует: {e}")
            except Exception as e:
                logger.error(f"Ошибка импорта файла {file_path}: {e}")
                raise
        
        logger.success("Импорт всех чеклистов завершен")
        
    finally:
        db.close()


async def validate_all_checklists():
    """Валидация всех файлов чеклистов без импорта"""
    
    logger.info("Валидация файлов чеклистов...")
    
    for file_path, description in CHECKLIST_FILES:
        full_path = Path(__file__).parent.parent.parent / file_path
        
        if not full_path.exists():
            logger.warning(f"Файл не найден: {full_path}")
            continue
        
        try:
            validation = checklist_service.validate_checklist_file(str(full_path))
            
            if validation["valid"]:
                summary = validation["summary"]
                logger.success(f"✅ {description}:")
                logger.info(f"   - Секций: {summary['total_sections']}")
                logger.info(f"   - Вопросов: {summary['total_questions']}")
                logger.info(f"   - Slug: {summary['slug']}")
            else:
                logger.error(f"❌ {description}: {validation['errors']}")
                
        except Exception as e:
            logger.error(f"Ошибка валидации {file_path}: {e}")


async def main():
    """Главная функция"""
    
    if len(sys.argv) > 1 and sys.argv[1] == "--validate-only":
        await validate_all_checklists()
    else:
        await import_checklist_files()


if __name__ == "__main__":
    asyncio.run(main())
