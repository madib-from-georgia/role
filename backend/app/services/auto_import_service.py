"""
Сервис для автоматического импорта чеклистов при старте приложения
"""

import asyncio
from pathlib import Path
from typing import List, Tuple
from sqlalchemy.orm import Session
from loguru import logger

from app.database.connection import SessionLocal
from app.services.checklist_service import checklist_service


class AutoImportService:
    """Сервис автоматического импорта чеклистов"""
    
    def __init__(self, checklist_file_path: str = "checklists_to_import.txt"):
        """
        Инициализация сервиса
        
        Args:
            checklist_file_path: Путь к файлу со списком чеклистов
        """
        self.root_path = Path(__file__).parent.parent.parent.parent
        self.checklist_file_path = self.root_path / checklist_file_path
    
    def load_checklist_list(self) -> List[str]:
        """
        Загружает список чеклистов из файла
        
        Returns:
            Список путей к файлам чеклистов
        """
        if not self.checklist_file_path.exists():
            logger.warning(f"Файл со списком чеклистов не найден: {self.checklist_file_path}")
            return []
        
        checklists = []
        
        try:
            with open(self.checklist_file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    
                    # Пропускаем пустые строки и комментарии
                    if not line or line.startswith('#'):
                        continue
                    
                    # Добавляем путь к файлу
                    checklists.append(line)
            
            logger.info(f"Загружено {len(checklists)} чеклистов для импорта")
            return checklists
            
        except Exception as e:
            logger.error(f"Ошибка чтения файла {self.checklist_file_path}: {e}")
            return []
    
    async def import_checklists_on_startup(self) -> None:
        """
        Импортирует чеклисты при старте приложения
        """
        logger.info("Начинаем автоматический импорт чеклистов...")
        
        checklists = self.load_checklist_list()
        if not checklists:
            logger.info("Нет чеклистов для импорта")
            return
        
        db: Session = SessionLocal()
        
        try:
            imported_count = 0
            skipped_count = 0
            
            for file_path in checklists:
                full_path = self.root_path / file_path
                
                if not full_path.exists():
                    logger.warning(f"Файл не найден: {full_path}")
                    continue
                
                try:
                    logger.info(f"Импорт чеклиста: {file_path}")
                    
                    # Сначала валидируем файл
                    validation = checklist_service.validate_checklist_file(str(full_path))
                    
                    if not validation["valid"]:
                        logger.error(f"Файл не прошел валидацию: {validation['errors']}")
                        continue
                    
                    # Импортируем в базу данных
                    checklist = checklist_service.import_checklist_from_file(db, str(full_path))
                    
                    logger.success(f"Чеклист '{checklist.title}' успешно импортирован (ID: {checklist.id})")
                    imported_count += 1
                    
                except ValueError as e:
                    if "уже существует" in str(e):
                        logger.info(f"Чеклист уже существует: {file_path}")
                        skipped_count += 1
                    else:
                        logger.error(f"Ошибка валидации: {e}")
                except Exception as e:
                    logger.error(f"Ошибка импорта файла {file_path}: {e}")
            
            logger.success(f"Автоматический импорт завершен. Импортировано: {imported_count}, пропущено: {skipped_count}")
            
        finally:
            db.close()
    
    async def manual_import_checklists(self) -> dict:
        """
        Ручной импорт чеклистов (для API endpoint)
        
        Returns:
            Словарь с результатами импорта
        """
        logger.info("Начинаем ручной импорт чеклистов...")
        
        checklists = self.load_checklist_list()
        if not checklists:
            return {
                "success": False,
                "message": "Нет чеклистов для импорта",
                "imported": 0,
                "skipped": 0,
                "errors": []
            }
        
        db: Session = SessionLocal()
        
        try:
            imported_count = 0
            skipped_count = 0
            errors = []
            
            for file_path in checklists:
                full_path = self.root_path / file_path
                
                if not full_path.exists():
                    error_msg = f"Файл не найден: {full_path}"
                    logger.warning(error_msg)
                    errors.append(error_msg)
                    continue
                
                try:
                    # Валидируем файл
                    validation = checklist_service.validate_checklist_file(str(full_path))
                    
                    if not validation["valid"]:
                        error_msg = f"Файл не прошел валидацию: {validation['errors']}"
                        logger.error(error_msg)
                        errors.append(error_msg)
                        continue
                    
                    # Импортируем в базу данных
                    checklist = checklist_service.import_checklist_from_file(db, str(full_path))
                    
                    logger.success(f"Чеклист '{checklist.title}' успешно импортирован (ID: {checklist.id})")
                    imported_count += 1
                    
                except ValueError as e:
                    if "уже существует" in str(e):
                        logger.info(f"Чеклист уже существует: {file_path}")
                        skipped_count += 1
                    else:
                        error_msg = f"Ошибка валидации: {e}"
                        logger.error(error_msg)
                        errors.append(error_msg)
                except Exception as e:
                    error_msg = f"Ошибка импорта файла {file_path}: {e}"
                    logger.error(error_msg)
                    errors.append(error_msg)
            
            return {
                "success": True,
                "message": f"Импорт завершен. Импортировано: {imported_count}, пропущено: {skipped_count}",
                "imported": imported_count,
                "skipped": skipped_count,
                "errors": errors
            }
            
        finally:
            db.close()


# Глобальный экземпляр сервиса
auto_import_service = AutoImportService()