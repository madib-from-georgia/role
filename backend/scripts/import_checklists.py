"""
Скрипт для импорта чеклистов из JSON файлов в базу данных

УСТАРЕЛ: Теперь используется автоматический импорт при старте приложения
и ручной импорт через API endpoint /api/checklists/import

Этот скрипт оставлен для обратной совместимости.
Теперь он использует новый AutoImportService для импорта чеклистов.
"""

import asyncio
import sys
from pathlib import Path

# Добавляем корневую директорию в Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.database.connection import init_db
from app.services.auto_import_service import auto_import_service
from loguru import logger


async def main():
    """Главная функция"""
    
    # Инициализируем базу данных
    await init_db()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--validate-only":
        logger.info("Режим валидации не поддерживается в новой версии")
        logger.info("Используйте API endpoint /api/checklists/import/status для получения информации")
        return
    
    logger.info("Запуск импорта чеклистов через AutoImportService...")
    
    try:
        result = await auto_import_service.manual_import_checklists()
        
        if result["success"]:
            logger.success(result["message"])
            if result["errors"]:
                logger.warning("Обнаружены ошибки:")
                for error in result["errors"]:
                    logger.error(f"  - {error}")
        else:
            logger.error(result["message"])
            
    except Exception as e:
        logger.error(f"Ошибка при импорте: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
