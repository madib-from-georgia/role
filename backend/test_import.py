#!/usr/bin/env python3
"""
Тестовый скрипт для проверки импорта нового JSON файла
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database.connection import SessionLocal
from app.services.checklist_service import checklist_service
from loguru import logger

def test_import():
    """Тестирование импорта нового JSON файла"""
    
    # Путь к тестовому JSON файлу
    json_file_path = "../docs/modules/01-physical-portrait/ACTOR_PHYSICAL_CHECKLIST_NEW_FORMAT.json"
    
    if not os.path.exists(json_file_path):
        logger.error(f"Файл не найден: {json_file_path}")
        return False
    
    logger.info(f"Тестирование импорта файла: {json_file_path}")
    
    # Создаем сессию базы данных
    db: Session = SessionLocal()
    
    try:
        # Импортируем чеклист
        checklist = checklist_service.import_checklist_from_file(db, json_file_path)
        
        logger.success(f"Чеклист успешно импортирован:")
        logger.info(f"  ID: {checklist.id}")
        logger.info(f"  External ID: {checklist.external_id}")
        logger.info(f"  Title: {checklist.title}")
        logger.info(f"  Slug: {checklist.slug}")
        logger.info(f"  File Hash: {checklist.file_hash}")
        logger.info(f"  Version: {checklist.version}")
        
        # Получаем полную структуру для проверки
        full_checklist = checklist_service.get_checklist_structure(db, checklist.slug)
        
        if full_checklist:
            logger.info(f"Структура чеклиста:")
            logger.info(f"  Секций: {len(full_checklist.sections)}")
            
            total_questions = 0
            total_answers = 0
            
            for section in full_checklist.sections:
                logger.info(f"    Секция '{section.title}': {len(section.subsections)} подсекций")
                
                for subsection in section.subsections:
                    for group in subsection.question_groups:
                        logger.info(f"      Группа '{group.title}': {len(group.questions)} вопросов")
                        total_questions += len(group.questions)
                        
                        for question in group.questions:
                            total_answers += len(question.answers)
                            logger.info(f"        Вопрос: {question.text[:50]}... ({len(question.answers)} ответов)")
            
            logger.success(f"Всего вопросов: {total_questions}")
            logger.success(f"Всего ответов: {total_answers}")
            
        return True
        
    except Exception as e:
        logger.error(f"Ошибка при импорте: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False
        
    finally:
        db.close()

if __name__ == "__main__":
    logger.info("Запуск тестирования импорта нового JSON файла")
    
    success = test_import()
    
    if success:
        logger.success("Тест импорта прошел успешно!")
        sys.exit(0)
    else:
        logger.error("Тест импорта завершился с ошибкой!")
        sys.exit(1)