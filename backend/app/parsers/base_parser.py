"""
Базовый класс для всех парсеров файлов.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class BaseParser(ABC):
    """Базовый класс для парсеров файлов."""
    
    def __init__(self):
        self.supported_extensions = []
        self.max_file_size = 50 * 1024 * 1024  # 50MB по умолчанию
    
    @abstractmethod
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """
        Парсинг файла.
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            Словарь с контентом и метаданными
        """
        pass
    
    @abstractmethod
    def validate_file(self, file_path: str) -> bool:
        """
        Валидация файла.
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            True если файл валиден, False иначе
        """
        pass
    
    def _validate_basic(self, file_path: str) -> bool:
        """Базовая валидация файла."""
        try:
            file_path_obj = Path(file_path)
            
            # Проверяем существование файла
            if not file_path_obj.exists():
                logger.error(f"Файл не существует: {file_path}")
                return False
            
            # Проверяем размер файла
            file_size = file_path_obj.stat().st_size
            if file_size > self.max_file_size:
                logger.error(f"Файл слишком большой: {file_size} байт (максимум {self.max_file_size})")
                return False
            
            # Проверяем расширение
            if self.supported_extensions and file_path_obj.suffix.lower() not in self.supported_extensions:
                logger.warning(f"Неожиданное расширение файла: {file_path_obj.suffix}")
            
            # Проверяем, что файл не пустой
            if file_size == 0:
                logger.error("Файл пустой")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка базовой валидации файла {file_path}: {e}")
            return False
    
    def _extract_basic_metadata(self, file_path: str, content: str) -> Dict[str, Any]:
        """Извлечение базовых метаданных."""
        file_path_obj = Path(file_path)
        
        return {
            'filename': file_path_obj.name,
            'file_size': file_path_obj.stat().st_size if file_path_obj.exists() else 0,
            'character_count': len(content),
            'word_count': len(content.split()),
            'line_count': len(content.split('\n')),
            'format': file_path_obj.suffix.lower().lstrip('.')
        }