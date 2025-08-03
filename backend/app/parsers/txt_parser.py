"""
Парсер TXT файлов.
Адаптировано из проекта analyse-text.
"""

import chardet
import logging
import re
from typing import Dict, Any
from pathlib import Path

from .base_parser import BaseParser

logger = logging.getLogger(__name__)


class TxtParser(BaseParser):
    """Парсер для TXT файлов"""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = ['.txt']
        self.max_file_size = 10 * 1024 * 1024  # 10MB для TXT файлов
        self.supported_encodings = [
            'cp1251',
            'utf-8',
            'windows-1251',
            'koi8-r',
            'iso-8859-1',
            'ascii'
        ]
    
    def detect_encoding(self, file_path: str) -> str:
        """Определение кодировки файла"""
        try:
            with open(file_path, 'rb') as file:
                raw_data = file.read()
                result = chardet.detect(raw_data)
                encoding = result['encoding']
                confidence = result['confidence']
                
                logger.info(f"Определена кодировка: {encoding} (уверенность: {confidence:.2%})")
                
                # Если уверенность низкая, пробуем стандартные кодировки
                if confidence and confidence < 0.7:
                    logger.warning(f"Низкая уверенность в кодировке {encoding}, пробуем стандартные")
                    return self._try_standard_encodings(file_path)
                
                return encoding or 'utf-8'
                
        except Exception as e:
            logger.error(f"Ошибка определения кодировки: {e}")
            return 'utf-8'
    
    def _try_standard_encodings(self, file_path: str) -> str:
        """Попытка чтения файла с различными кодировками"""
        for encoding in self.supported_encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    # Пробуем прочитать первые 1000 символов
                    f.read(1000)
                logger.info(f"Успешно определена кодировка: {encoding}")
                return encoding
            except UnicodeDecodeError:
                continue
            except Exception:
                continue
        
        logger.warning("Не удалось определить кодировку, используем UTF-8")
        return 'utf-8'
    
    def clean_text(self, text: str) -> str:
        """Очистка и нормализация текста"""
        if not text:
            return ""
        
        # Удаляем лишние пробелы и переносы строк
        text = text.strip()
        
        # Нормализуем переносы строк
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # Удаляем множественные пробелы
        text = re.sub(r' +', ' ', text)
        
        # Удаляем множественные переносы строк (оставляем максимум 2)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Удаляем пробелы в начале и конце строк
        lines = text.split('\n')
        lines = [line.strip() for line in lines]
        text = '\n'.join(lines)
        
        return text
    
    def extract_metadata(self, file_path: str, content: str) -> Dict[str, Any]:
        """Извлечение метаданных из файла"""
        # Получаем базовые метаданные
        metadata = self._extract_basic_metadata(file_path, content)
        
        # Добавляем специфичные для TXT
        metadata.update({
            'encoding': self.detect_encoding(file_path),
            'format': 'txt'
        })
        
        # Пытаемся извлечь дополнительную информацию из содержимого
        lines = content.split('\n')
        
        # Ищем заголовок (первая непустая строка)
        title = None
        for line in lines[:10]:  # Ищем в первых 10 строках
            line = line.strip()
            if line and len(line) < 100:  # Заголовок обычно короткий
                title = line
                break
        
        if title:
            metadata['title'] = title
        
        # Ищем автора (паттерны типа "Автор: Имя" или просто имя в начале)
        author = None
        for line in lines[:20]:  # Ищем в первых 20 строках
            line = line.strip()
            if any(keyword in line.lower() for keyword in ['автор:', 'author:', 'написал', 'сочинение']):
                # Извлекаем имя автора
                parts = line.split(':')
                if len(parts) > 1:
                    author = parts[1].strip()
                    break
        
        if author:
            metadata['author'] = author
        
        # Примерная оценка жанра по ключевым словам
        text_lower = content.lower()
        genre_keywords = {
            'роман': 'роман',
            'повесть': 'повесть', 
            'рассказ': 'рассказ',
            'стих': 'поэзия',
            'поэма': 'поэзия',
            'драма': 'драма',
            'комедия': 'комедия'
        }
        
        for keyword, genre in genre_keywords.items():
            if keyword in text_lower:
                metadata['genre'] = genre
                break
        
        return metadata
    
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """Парсинг TXT файла"""
        try:
            # Определяем кодировку
            encoding = self.detect_encoding(file_path)
            
            # Читаем файл
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            # Очищаем текст
            content = self.clean_text(content)
            
            # Извлекаем метаданные
            metadata = self.extract_metadata(file_path, content)
            
            return {
                'content': content,
                'metadata': metadata
            }
            
        except Exception as e:
            logger.error(f"Ошибка парсинга TXT файла {file_path}: {e}")
            raise ValueError(f"Ошибка чтения TXT файла: {e}")
    
    def validate_file(self, file_path: str) -> bool:
        """Валидация TXT файла"""
        try:
            # Базовая валидация
            if not self._validate_basic(file_path):
                return False
            
            # Пробуем прочитать первые несколько байт
            with open(file_path, 'rb') as file:
                first_bytes = file.read(100)
                if not first_bytes:
                    logger.error("Файл пустой")
                    return False
            
            # Проверяем, что можем определить кодировку
            encoding = self.detect_encoding(file_path)
            if not encoding:
                logger.error("Не удалось определить кодировку файла")
                return False
            
            # Пробуем прочитать файл с определенной кодировкой
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    f.read(100)  # Читаем первые 100 символов
            except UnicodeDecodeError:
                logger.error(f"Не удалось прочитать файл с кодировкой {encoding}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка валидации TXT файла {file_path}: {e}")
            return False


# Глобальный экземпляр парсера
txt_parser = TxtParser()


def parse_txt_file(file_path: str) -> Dict[str, Any]:
    """Функция-обертка для парсинга TXT файла"""
    return txt_parser.parse_file(file_path)


def validate_txt_file(file_path: str) -> bool:
    """Функция-обертка для валидации TXT файла"""
    return txt_parser.validate_file(file_path)
