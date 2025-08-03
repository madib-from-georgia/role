"""
Парсер FB2 файлов.
Адаптировано из проекта analyse-text.
"""

import xml.etree.ElementTree as ET
import logging
import re
from typing import Dict, Any, Optional
from pathlib import Path

from .base_parser import BaseParser

logger = logging.getLogger(__name__)


class FB2Parser(BaseParser):
    """Парсер для FB2 файлов"""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = ['.fb2']
        self.max_file_size = 20 * 1024 * 1024  # 20MB для FB2 файлов
        
        # Пространства имен FB2
        self.namespaces = {
            'fb': 'http://www.gribuser.ru/xml/fictionbook/2.0',
            'xlink': 'http://www.w3.org/1999/xlink'
        }
    
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
    
    def extract_text_from_element(self, element) -> str:
        """Извлечение текста из XML элемента"""
        if element is None:
            return ""
        
        # Собираем весь текст из элемента и его потомков
        text_parts = []
        
        # Текст самого элемента
        if element.text:
            text_parts.append(element.text.strip())
        
        # Текст всех дочерних элементов
        for child in element:
            child_text = self.extract_text_from_element(child)
            if child_text:
                text_parts.append(child_text)
            
            # Текст после дочернего элемента
            if child.tail:
                text_parts.append(child.tail.strip())
        
        return ' '.join(text_parts)
    
    def extract_metadata(self, root) -> Dict[str, Any]:
        """Извлечение метаданных из FB2"""
        metadata = {'fb2_info': {}}
        
        # Ищем информацию о книге
        title_info = root.find('.//fb:title-info', self.namespaces)
        
        if title_info is not None:
            # Автор(ы)
            authors = title_info.findall('.//fb:author', self.namespaces)
            if authors:
                author_names = []
                for author in authors:
                    first_name = author.find('fb:first-name', self.namespaces)
                    middle_name = author.find('fb:middle-name', self.namespaces)
                    last_name = author.find('fb:last-name', self.namespaces)
                    
                    name_parts = []
                    if first_name is not None and first_name.text:
                        name_parts.append(first_name.text)
                    if middle_name is not None and middle_name.text:
                        name_parts.append(middle_name.text)
                    if last_name is not None and last_name.text:
                        name_parts.append(last_name.text)
                    
                    if name_parts:
                        author_names.append(' '.join(name_parts))
                
                if author_names:
                    metadata['fb2_info']['authors'] = author_names
            
            # Название книги
            book_title = title_info.find('fb:book-title', self.namespaces)
            if book_title is not None and book_title.text:
                metadata['fb2_info']['title'] = book_title.text.strip()
            
            # Жанры
            genres = title_info.findall('fb:genre', self.namespaces)
            if genres:
                genre_list = [g.text.strip() for g in genres if g.text]
                if genre_list:
                    metadata['fb2_info']['genres'] = genre_list
            
            # Аннотация
            annotation = title_info.find('fb:annotation', self.namespaces)
            if annotation is not None:
                annotation_text = self.extract_text_from_element(annotation)
                if annotation_text:
                    metadata['fb2_info']['annotation'] = annotation_text
            
            # Ключевые слова
            keywords = title_info.find('fb:keywords', self.namespaces)
            if keywords is not None and keywords.text:
                metadata['fb2_info']['keywords'] = keywords.text.strip()
            
            # Дата написания
            date = title_info.find('fb:date', self.namespaces)
            if date is not None and date.text:
                metadata['fb2_info']['date'] = date.text.strip()
            
            # Язык
            lang = title_info.find('fb:lang', self.namespaces)
            if lang is not None and lang.text:
                metadata['fb2_info']['language'] = lang.text.strip()
        
        # Информация о документе
        document_info = root.find('.//fb:document-info', self.namespaces)
        if document_info is not None:
            # Программа создания
            program = document_info.find('fb:program-used', self.namespaces)
            if program is not None and program.text:
                metadata['fb2_info']['program_used'] = program.text.strip()
            
            # Дата создания документа
            doc_date = document_info.find('fb:date', self.namespaces)
            if doc_date is not None:
                doc_date_value = doc_date.get('value') or doc_date.text
                if doc_date_value:
                    metadata['fb2_info']['document_date'] = doc_date_value.strip()
        
        return metadata
    
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """Парсинг FB2 файла"""
        try:
            # Парсим XML
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Извлекаем основной текст
            body = root.find('.//fb:body', self.namespaces)
            
            content_parts = []
            
            if body is not None:
                # Обходим все элементы в теле документа
                for element in body.iter():
                    # Собираем текст из параграфов, заголовков и других текстовых элементов
                    if element.tag.endswith('}p') or element.tag.endswith('}v') or element.tag.endswith('}title'):
                        text = self.extract_text_from_element(element)
                        if text.strip():
                            content_parts.append(text.strip())
                    elif element.text and element.text.strip():
                        # Добавляем прямой текст элементов
                        content_parts.append(element.text.strip())
            
            # Объединяем и очищаем текст
            content = '\n'.join(content_parts)
            content = self.clean_text(content)
            
            # Извлекаем метаданные
            metadata = self.extract_metadata(root)
            
            # Добавляем базовые метаданные
            basic_metadata = self._extract_basic_metadata(file_path, content)
            metadata.update(basic_metadata)
            metadata['format'] = 'fb2'
            
            return {
                'content': content,
                'metadata': metadata
            }
            
        except ET.ParseError as e:
            logger.error(f"Ошибка парсинга XML в FB2 файле {file_path}: {e}")
            raise ValueError(f"Файл не является валидным FB2: {e}")
        except Exception as e:
            logger.error(f"Ошибка парсинга FB2 файла {file_path}: {e}")
            raise ValueError(f"Ошибка чтения FB2 файла: {e}")
    
    def validate_file(self, file_path: str) -> bool:
        """Валидация FB2 файла"""
        try:
            # Базовая валидация
            if not self._validate_basic(file_path):
                return False
            
            # Проверяем, что это валидный XML
            try:
                tree = ET.parse(file_path)
                root = tree.getroot()
                
                # Проверяем, что это FB2 файл
                expected_tag = '{http://www.gribuser.ru/xml/fictionbook/2.0}FictionBook'
                if root.tag != expected_tag:
                    logger.error(f"Файл не является валидным FB2. Корневой элемент: {root.tag}")
                    return False
                
                # Проверяем наличие обязательных элементов
                description = root.find('.//fb:description', self.namespaces)
                if description is None:
                    logger.warning("FB2 файл не содержит элемент description")
                
                body = root.find('.//fb:body', self.namespaces)
                if body is None:
                    logger.error("FB2 файл не содержит элемент body")
                    return False
                
            except ET.ParseError as e:
                logger.error(f"Файл не является валидным XML: {e}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка валидации FB2 файла {file_path}: {e}")
            return False


# Глобальный экземпляр парсера
fb2_parser = FB2Parser()


def parse_fb2_file(file_path: str) -> Dict[str, Any]:
    """Функция-обертка для парсинга FB2 файла"""
    return fb2_parser.parse_file(file_path)


def validate_fb2_file(file_path: str) -> bool:
    """Функция-обертка для валидации FB2 файла"""
    return fb2_parser.validate_file(file_path)
