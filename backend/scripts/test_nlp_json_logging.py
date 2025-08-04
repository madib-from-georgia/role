#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы системы JSON логирования NLP результатов
"""

import sys
import asyncio
from pathlib import Path

# Добавляем путь к backend для импортов
backend_path = Path(__file__).parent.parent
sys.path.append(str(backend_path))

from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.crud import text as text_crud
from app.services.nlp_processor import get_nlp_processor
from loguru import logger

async def test_nlp_json_logging():
    """Тестирование системы JSON логирования"""
    
    logger.info("=== Тест системы JSON логирования NLP ===")
    
    # Получаем сессию БД
    db: Session = next(get_db())
    
    try:
        # Ищем любой текст в БД для тестирования
        texts = text_crud.get_multi(db, limit=5)
        
        if not texts:
            logger.warning("В БД нет текстов для тестирования")
            return
        
        # Берем первый текст
        test_text = texts[0]
        logger.info(f"Тестируем на тексте: {test_text.filename} (ID: {test_text.id})")
        
        # Получаем процессор NLP
        nlp_processor = get_nlp_processor()
        
        # Принудительно переобрабатываем текст, чтобы создать JSON логи
        logger.info("Запускаю NLP анализ...")
        result = await nlp_processor.process_text(
            text_id=test_text.id,
            db=db,
            force_reprocess=True
        )
        
        logger.success(f"Анализ завершен! Найдено {len(result.characters)} персонажей")
        
        # Проверяем, что файлы созданы
        logs_dir = Path(__file__).parent.parent / "logs"
        
        logger.info(f"Проверяю созданные файлы в: {logs_dir}")
        
        if logs_dir.exists():
            # Проверяем структуру
            latest_dir = logs_dir / "latest"
            if latest_dir.exists():
                latest_files = list(latest_dir.glob("*.json"))
                logger.info(f"Файлы в latest/: {[f.name for f in latest_files]}")
            
            # Проверяем папки для книг
            book_dirs = [d for d in logs_dir.iterdir() if d.is_dir() and d.name != "latest"]
            for book_dir in book_dirs:
                book_files = list(book_dir.glob("*.json"))
                logger.info(f"Файлы в {book_dir.name}/: {[f.name for f in book_files]}")
        
        logger.success("✅ Тест системы JSON логирования завершен успешно!")
        
    except Exception as e:
        logger.error(f"Ошибка при тестировании: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_nlp_json_logging())