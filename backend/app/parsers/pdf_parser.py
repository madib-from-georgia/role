"""
Парсер PDF файлов.
"""

import logging
import re
from typing import Dict, Any
from pathlib import Path
from pypdf import PdfReader

from .base_parser import BaseParser
from .content_models import StructuredContent

logger = logging.getLogger(__name__)


class PDFParser(BaseParser):
    """Парсер для PDF файлов"""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = ['.pdf']
        self.max_file_size = 50 * 1024 * 1024  # 50MB для PDF файлов
    
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
        
        # Удаляем артефакты PDF (номера страниц, заголовки)
        text = self._remove_pdf_artifacts(text)
        
        return text
    
    def _remove_pdf_artifacts(self, text: str) -> str:
        """Удаление типичных артефактов PDF"""
        lines = text.split('\n')
        clean_lines = []
        
        for line in lines:
            line = line.strip()
            
            # Пропускаем очень короткие строки (возможно номера страниц)
            if len(line) < 3:
                continue
            
            # Пропускаем строки состоящие только из цифр (номера страниц)
            if line.isdigit():
                continue
            
            # Пропускаем строки с типичными паттернами заголовков/подвалов
            if re.match(r'^(стр\.|page|глава|chapter)\s*\d+', line.lower()):
                continue
            
            clean_lines.append(line)
        
        return '\n'.join(clean_lines)
    
    def extract_metadata(self, file_path: str, content: str, pdf_info: Dict) -> Dict[str, Any]:
        """Извлечение метаданных из PDF"""
        # Получаем базовые метаданные
        metadata = self._extract_basic_metadata(file_path, content)
        
        # Добавляем специфичные для PDF
        metadata.update({
            'format': 'pdf',
            'pdf_info': {}
        })
        
        # Извлекаем метаданные PDF
        if pdf_info:
            for key, value in pdf_info.items():
                if value:
                    clean_key = key.replace('/', '').lower()
                    metadata['pdf_info'][clean_key] = str(value).strip()
        
        # Пытаемся извлечь дополнительную информацию из содержимого
        lines = content.split('\n')
        
        # Ищем заголовок (одна из первых непустых строк)
        title = None
        for line in lines[:20]:  # Ищем в первых 20 строках
            line = line.strip()
            if line and len(line) > 5 and len(line) < 200:  # Разумная длина заголовка
                # Исключаем строки с датами, номерами
                if not re.search(r'\d{4}|\d+\.\d+|\d+/\d+', line):
                    title = line
                    break
        
        if title and 'title' not in metadata['pdf_info']:
            metadata['pdf_info']['title'] = title
        
        # Ищем автора в тексте
        author = None
        for line in lines[:30]:  # Ищем в первых 30 строках
            line = line.strip()
            author_patterns = [
                r'автор[:\s]+([а-я\s\.]+)',
                r'author[:\s]+([a-z\s\.]+)',
                r'написал[:\s]+([а-я\s\.]+)',
                r'сочинение[:\s]+([а-я\s\.]+)'
            ]
            
            for pattern in author_patterns:
                match = re.search(pattern, line.lower())
                if match:
                    author = match.group(1).strip()
                    break
            
            if author:
                break
        
        if author and 'author' not in metadata['pdf_info']:
            metadata['pdf_info']['author'] = author
        
        return metadata
    
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """Парсинг PDF файла"""
        try:
            content_parts = []
            pdf_info = {}
            page_count = 0
            
            with open(file_path, 'rb') as f:
                reader = PdfReader(f)
                page_count = len(reader.pages)
                
                # Извлекаем текст из всех страниц
                for page_num, page in enumerate(reader.pages):
                    try:
                        text = page.extract_text()
                        if text and text.strip():
                            content_parts.append(text.strip())
                    except Exception as e:
                        logger.warning(f"Ошибка извлечения текста со страницы {page_num + 1}: {e}")
                        continue
                
                # Получаем метаданные PDF
                if reader.metadata:
                    for key, value in reader.metadata.items():
                        if value:
                            pdf_info[key] = value
            
            if not content_parts:
                raise ValueError("Не удалось извлечь текст из PDF файла")
            
            # Объединяем и очищаем текст
            content = '\n\n'.join(content_parts)
            content = self.clean_text(content)
            
            # Извлекаем метаданные
            metadata = self.extract_metadata(file_path, content, pdf_info)
            metadata['pdf_info']['page_count'] = page_count
            
            return {
                'content': content,
                'metadata': metadata
            }
            
        except Exception as e:
            logger.error(f"Ошибка парсинга PDF файла {file_path}: {e}")
            raise ValueError(f"Ошибка чтения PDF файла: {e}")
    
    def parse_to_structured_content(self, file_path: str) -> StructuredContent:
        """
        Парсинг PDF файла в структурированный формат.
        """
        try:
            # Используем стандартный парсинг
            result = self.parse_file(file_path)
            content = result['content']
            metadata = result['metadata']
            
            # Создаем структурированный контент используя базовую реализацию
            return self._create_structured_content_from_text(content, metadata, file_path)
            
        except Exception as e:
            logger.error(f"Ошибка парсинга PDF файла {file_path}: {e}")
            raise ValueError(f"Ошибка чтения PDF файла: {e}")
    
    def validate_file(self, file_path: str) -> bool:
        """Валидация PDF файла"""
        try:
            # Базовая валидация
            if not self._validate_basic(file_path):
                return False
            
            # Проверяем, что это валидный PDF
            try:
                with open(file_path, 'rb') as f:
                    reader = PdfReader(f)
                    
                    # Проверяем, что есть страницы
                    if len(reader.pages) == 0:
                        logger.error("PDF файл не содержит страниц")
                        return False
                    
                    # Пробуем извлечь текст с первой страницы
                    try:
                        first_page = reader.pages[0]
                        text = first_page.extract_text()
                        # PDF может быть валидным, но без извлекаемого текста (например, только изображения)
                        if not text or not text.strip():
                            logger.warning("PDF файл не содержит извлекаемого текста")
                            # Не возвращаем False, так как это может быть валидный PDF с изображениями
                    except Exception as e:
                        logger.warning(f"Ошибка извлечения текста из PDF: {e}")
                
            except Exception as e:
                logger.error(f"Файл не является валидным PDF: {e}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка валидации PDF файла {file_path}: {e}")
            return False


# Глобальный экземпляр парсера
pdf_parser = PDFParser()


def parse_pdf_file(file_path: str) -> Dict[str, Any]:
    """Функция-обертка для парсинга PDF файла"""
    return pdf_parser.parse_file(file_path)


def validate_pdf_file(file_path: str) -> bool:
    """Функция-обертка для валидации PDF файла"""
    return pdf_parser.validate_file(file_path)
