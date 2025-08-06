"""
Скрипт для импорта чеклистов из JSON файлов в базу данных

Поддерживает структуру JSON с полями:
- title: заголовок чеклиста
- goal: цель чеклиста (объект с title и description)
- sections: массив секций с подсекциями, группами вопросов и вопросами
- Каждый вопрос содержит: question, options, optionsType, source, hint

Источники ответов (source): text, logic, imagination
Типы вариантов (optionsType): single, multiple, none
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
    ("docs/modules/01-physical-portrait/ACTOR_PHYSICAL_CHECKLIST.json", "Физический портрет персонажа"),
    # ("docs/modules/02-emotional-profile/ACTOR_EMOTIONAL_CHECKLIST.json", "Эмоциональный профиль персонажа"),
    # ("docs/modules/03-speech-characteristics/ACTOR_SPEECH_CHECKLIST.json", "Речевая характеристика персонажа"),
    # ("docs/modules/04-internal-conflicts/ACTOR_INTERNAL_CONFLICTS_CHECKLIST.json", "Внутренние конфликты персонажа"),
    # ("docs/modules/05-motivation-goals/ACTOR_MOTIVATION_GOALS_CHECKLIST.json", "Мотивация и цели персонажа"),
    # ("docs/modules/06-character-relationships/ACTOR_RELATIONSHIPS_CHECKLIST.json", "Отношения персонажа"),
    # ("docs/modules/07-biography-backstory/ACTOR_BIOGRAPHY_CHECKLIST.json", "Биография и предыстория персонажа"),
    # ("docs/modules/08-social-status/ACTOR_SOCIAL_STATUS_CHECKLIST.json", "Социальный статус персонажа"),
    # ("docs/modules/09-key-scenes/ACTOR_KEY_SCENES_CHECKLIST.json", "Ключевые сцены персонажа"),
    # ("docs/modules/10-acting-tasks/ACTOR_ACTING_TASKS_CHECKLIST.json", "Актерские задачи"),
    # ("docs/modules/11-practical-exercises/ACTOR_PRACTICAL_EXERCISES_CHECKLIST.json", "Практические упражнения"),
    # ("docs/modules/12-subtext-analysis/ACTOR_SUBTEXT_CHECKLIST.json", "Анализ подтекста"),
    # ("docs/modules/13-tempo-rhythm/ACTOR_TEMPO_RHYTHM_CHECKLIST.json", "Темп и ритм персонажа"),
    # ("docs/modules/14-personality-type/ACTOR_PERSONALITY_TYPE_CHECKLIST.json", "Тип личности персонажа"),
    # ("docs/modules/15-defense-mechanisms/ACTOR_DEFENSE_MECHANISMS_CHECKLIST.json", "Защитные механизмы"),
    # ("docs/modules/16-trauma-ptsd/ACTOR_TRAUMA_PTSD_CHECKLIST.json", "Травма и ПТСР"),
    # ("docs/modules/17-archetypes/ACTOR_ARCHETYPES_CHECKLIST.json", "Архетипы персонажа"),
    # ("docs/modules/18-emotional-intelligence/ACTOR_EMOTIONAL_INTELLIGENCE_CHECKLIST.json", "Эмоциональный интеллект"),
    # ("docs/modules/19-cognitive-distortions/ACTOR_COGNITIVE_DISTORTIONS_CHECKLIST.json", "Когнитивные искажения"),
    # ("docs/modules/20-attachment-styles/ACTOR_ATTACHMENT_STYLES_CHECKLIST.json", "Стили привязанности")
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
