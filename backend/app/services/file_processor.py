"""
Сервис для обработки загружаемых файлов.
Использует специализированные парсеры для каждого формата.
"""

import os
import tempfile
import logging
from typing import Dict, Any
from pathlib import Path
from fastapi import UploadFile

from app.parsers import (
    TxtParser, FB2Parser, PDFParser, EPUBParser,
    parse_txt_file, parse_fb2_file, parse_pdf_file, parse_epub_file,
    validate_txt_file, validate_fb2_file, validate_pdf_file, validate_epub_file
)

logger = logging.getLogger(__name__)


class FileProcessor:
    """Основной класс для обработки различных типов файлов."""
    
    def __init__(self):
        self.supported_formats = ['txt', 'pdf', 'fb2', 'epub']
        self.max_file_size = 50 * 1024 * 1024  # 50MB
        
        # Инициализируем парсеры
        self.parsers = {
            'txt': TxtParser(),
            'pdf': PDFParser(),
            'fb2': FB2Parser(),
            'epub': EPUBParser()
        }
        
        # Функции парсинга (используем структурированные методы с нормализацией)
        self.parse_functions = {
            'txt': self._parse_txt_to_structured,
            'pdf': self._parse_pdf_to_structured,
            'fb2': self._parse_fb2_to_structured,
            'epub': self._parse_epub_to_structured
        }
        
        # Функции валидации
        self.validate_functions = {
            'txt': validate_txt_file,
            'pdf': validate_pdf_file,
            'fb2': validate_fb2_file,
            'epub': validate_epub_file
        }
    
    async def process_file(self, file: UploadFile) -> Dict[str, Any]:
        """
        Обработка загруженного файла с использованием специализированных парсеров.
        
        Returns:
            Dict with keys: content, metadata, filename, format
        """
        # Валидация файла
        self._validate_file(file)
        
        # Определяем формат файла
        file_format = self._get_file_format(file.filename)
        
        # Создаем временный файл
        temp_file_path = await self._save_temp_file(file)
        
        try:
            # Валидируем файл через специализированный парсер
            if not self.validate_functions[file_format](temp_file_path):
                raise ValueError(f"Файл не прошел валидацию для формата {file_format}")
            
            # Парсим файл через специализированный парсер
            result = self.parse_functions[file_format](temp_file_path)
            
            # Добавляем общую информацию
            result.update({
                'filename': file.filename,
                'original_format': file_format,
                'file_size': file.size
            })
            
            # Обновляем метаданные
            if 'metadata' in result:
                result['metadata']['original_filename'] = file.filename
                result['metadata']['upload_file_size'] = file.size
            
            return result
            
        finally:
            # Удаляем временный файл
            try:
                os.unlink(temp_file_path)
            except Exception as e:
                logger.warning(f"Не удалось удалить временный файл {temp_file_path}: {e}")
    
    def _parse_txt_to_structured(self, file_path: str) -> Dict[str, Any]:
        """Парсинг TXT файла с нормализацией контента"""
        try:
            structured_content = self.parsers['txt'].parse_to_structured_content(file_path)
            return {
                'content': structured_content.raw_content,  # Уже нормализованный контент
                'metadata': structured_content.metadata
            }
        except Exception as e:
            logger.warning(f"Ошибка структурированного парсинга TXT, используем fallback: {e}")
            # Fallback на старый метод
            return parse_txt_file(file_path)
    
    def _parse_pdf_to_structured(self, file_path: str) -> Dict[str, Any]:
        """Парсинг PDF файла с нормализацией контента"""
        try:
            structured_content = self.parsers['pdf'].parse_to_structured_content(file_path)
            return {
                'content': structured_content.raw_content,  # Уже нормализованный контент
                'metadata': structured_content.metadata
            }
        except Exception as e:
            logger.warning(f"Ошибка структурированного парсинга PDF, используем fallback: {e}")
            # Fallback на старый метод
            return parse_pdf_file(file_path)
    
    def _parse_fb2_to_structured(self, file_path: str) -> Dict[str, Any]:
        """Парсинг FB2 файла с нормализацией контента"""
        try:
            structured_content = self.parsers['fb2'].parse_to_structured_content(file_path)
            return {
                'content': structured_content.raw_content,  # Уже нормализованный контент
                'metadata': structured_content.metadata
            }
        except Exception as e:
            logger.warning(f"Ошибка структурированного парсинга FB2, используем fallback: {e}")
            # Fallback на старый метод
            return parse_fb2_file(file_path)
    
    def _parse_epub_to_structured(self, file_path: str) -> Dict[str, Any]:
        """Парсинг EPUB файла с нормализацией контента"""
        try:
            structured_content = self.parsers['epub'].parse_to_structured_content(file_path)
            return {
                'content': structured_content.raw_content,  # Уже нормализованный контент
                'metadata': structured_content.metadata
            }
        except Exception as e:
            logger.warning(f"Ошибка структурированного парсинга EPUB, используем fallback: {e}")
            # Fallback на старый метод
            return parse_epub_file(file_path)
    
    def _validate_file(self, file: UploadFile) -> None:
        """Валидация загружаемого файла."""
        if not file.filename:
            raise ValueError("Имя файла не указано")
        
        if file.size and file.size > self.max_file_size:
            raise ValueError(f"Размер файла превышает максимально допустимый ({self.max_file_size} байт)")
        
        file_format = self._get_file_format(file.filename)
        if file_format not in self.supported_formats:
            raise ValueError(f"Неподдерживаемый формат файла. Поддерживаются: {', '.join(self.supported_formats)}")
    
    def _get_file_format(self, filename: str) -> str:
        """Определение формата файла по расширению."""
        if not filename:
            raise ValueError("Имя файла не указано")
        
        extension = filename.split('.')[-1].lower()
        return extension
    
    async def _save_temp_file(self, file: UploadFile) -> str:
        """Сохранение файла во временную директорию."""
        file_format = self._get_file_format(file.filename)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_format}') as temp_file:
            content = await file.read()
            temp_file.write(content)
            return temp_file.name
    



# Создаем экземпляр процессора для использования в роутерах
file_processor = FileProcessor()
