"""
Парсер EPUB файлов.
"""

import logging
import re
import zipfile
from typing import Dict, Any, List
from pathlib import Path
from bs4 import BeautifulSoup

from .base_parser import BaseParser

logger = logging.getLogger(__name__)


class EPUBParser(BaseParser):
    """Парсер для EPUB файлов"""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = ['.epub']
        self.max_file_size = 100 * 1024 * 1024  # 100MB для EPUB файлов
    
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
    
    def extract_metadata_from_opf(self, opf_content: str) -> Dict[str, Any]:
        """Извлечение метаданных из OPF файла"""
        metadata = {}
        
        try:
            soup = BeautifulSoup(opf_content, 'xml')
            
            # Извлекаем заголовок
            title = soup.find('dc:title')
            if title:
                metadata['title'] = title.get_text().strip()
            
            # Извлекаем автора(ов)
            creators = soup.find_all('dc:creator')
            if creators:
                authors = []
                for creator in creators:
                    author_name = creator.get_text().strip()
                    if author_name:
                        authors.append(author_name)
                if authors:
                    metadata['authors'] = authors
            
            # Извлекаем язык
            language = soup.find('dc:language')
            if language:
                metadata['language'] = language.get_text().strip()
            
            # Извлекаем издателя
            publisher = soup.find('dc:publisher')
            if publisher:
                metadata['publisher'] = publisher.get_text().strip()
            
            # Извлекаем дату
            date = soup.find('dc:date')
            if date:
                metadata['date'] = date.get_text().strip()
            
            # Извлекаем описание
            description = soup.find('dc:description')
            if description:
                metadata['description'] = description.get_text().strip()
            
            # Извлекаем идентификаторы
            identifiers = soup.find_all('dc:identifier')
            if identifiers:
                ids = {}
                for identifier in identifiers:
                    scheme = identifier.get('opf:scheme') or identifier.get('scheme')
                    if scheme:
                        ids[scheme.lower()] = identifier.get_text().strip()
                    else:
                        ids['unknown'] = identifier.get_text().strip()
                if ids:
                    metadata['identifiers'] = ids
            
            # Извлекаем права
            rights = soup.find('dc:rights')
            if rights:
                metadata['rights'] = rights.get_text().strip()
            
        except Exception as e:
            logger.warning(f"Ошибка извлечения метаданных из OPF: {e}")
        
        return metadata
    
    def get_content_files(self, epub_zip: zipfile.ZipFile) -> List[str]:
        """Получение списка файлов с содержимым"""
        file_list = epub_zip.namelist()
        
        # Ищем файлы с содержимым (обычно .html или .xhtml)
        content_files = []
        
        for file_path in file_list:
            file_path_lower = file_path.lower()
            
            # Файлы содержимого
            if (file_path_lower.endswith(('.html', '.xhtml', '.htm')) and 
                not file_path_lower.endswith('toc.html') and 
                'nav' not in file_path_lower and
                'cover' not in file_path_lower):
                content_files.append(file_path)
        
        # Сортируем файлы по имени для логичного порядка
        content_files.sort()
        
        return content_files
    
    def extract_text_from_html(self, html_content: str) -> str:
        """Извлечение текста из HTML"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Удаляем скрипты, стили и другие нетекстовые элементы
            for element in soup(['script', 'style', 'meta', 'link']):
                element.decompose()
            
            # Извлекаем текст
            text = soup.get_text()
            
            return text.strip()
            
        except Exception as e:
            logger.warning(f"Ошибка извлечения текста из HTML: {e}")
            return ""
    
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """Парсинг EPUB файла"""
        try:
            content_parts = []
            metadata = {'epub_info': {}}
            
            with zipfile.ZipFile(file_path, 'r') as epub_zip:
                file_list = epub_zip.namelist()
                
                # Извлекаем метаданные из OPF файла
                opf_files = [f for f in file_list if f.endswith('.opf')]
                if opf_files:
                    try:
                        with epub_zip.open(opf_files[0]) as f:
                            opf_content = f.read().decode('utf-8', errors='ignore')
                            epub_metadata = self.extract_metadata_from_opf(opf_content)
                            metadata['epub_info'].update(epub_metadata)
                    except Exception as e:
                        logger.warning(f"Не удалось извлечь метаданные из OPF: {e}")
                
                # Получаем файлы с содержимым
                content_files = self.get_content_files(epub_zip)
                
                if not content_files:
                    raise ValueError("Не найдены файлы с содержимым в EPUB архиве")
                
                # Читаем содержимое из HTML файлов
                for content_file in content_files:
                    try:
                        with epub_zip.open(content_file) as f:
                            html_content = f.read().decode('utf-8', errors='ignore')
                            
                            # Извлекаем текст из HTML
                            text = self.extract_text_from_html(html_content)
                            
                            if text.strip():
                                content_parts.append(text.strip())
                                
                    except Exception as e:
                        logger.warning(f"Не удалось обработать файл {content_file}: {e}")
                        continue
            
            if not content_parts:
                raise ValueError("Не удалось извлечь содержимое из EPUB файла")
            
            # Объединяем и очищаем текст
            content = '\n\n'.join(content_parts)
            content = self.clean_text(content)
            
            # Добавляем базовые метаданные
            basic_metadata = self._extract_basic_metadata(file_path, content)
            metadata.update(basic_metadata)
            metadata['format'] = 'epub'
            metadata['epub_info']['file_count'] = len(content_files)
            
            return {
                'content': content,
                'metadata': metadata
            }
            
        except zipfile.BadZipFile:
            logger.error(f"Файл {file_path} не является валидным ZIP архивом")
            raise ValueError("Файл не является валидным EPUB (не ZIP архив)")
        except Exception as e:
            logger.error(f"Ошибка парсинга EPUB файла {file_path}: {e}")
            raise ValueError(f"Ошибка чтения EPUB файла: {e}")
    
    def validate_file(self, file_path: str) -> bool:
        """Валидация EPUB файла"""
        try:
            # Базовая валидация
            if not self._validate_basic(file_path):
                return False
            
            # Проверяем, что это валидный ZIP архив
            try:
                with zipfile.ZipFile(file_path, 'r') as epub_zip:
                    file_list = epub_zip.namelist()
                    
                    # Проверяем наличие обязательного файла mimetype
                    if 'mimetype' not in file_list:
                        logger.warning("EPUB файл не содержит файл mimetype")
                    else:
                        # Проверяем содержимое mimetype
                        try:
                            with epub_zip.open('mimetype') as f:
                                mimetype = f.read().decode('utf-8').strip()
                                if mimetype != 'application/epub+zip':
                                    logger.warning(f"Неверный mimetype: {mimetype}")
                        except Exception:
                            logger.warning("Не удалось прочитать mimetype")
                    
                    # Проверяем наличие META-INF/container.xml
                    container_xml = 'META-INF/container.xml'
                    if container_xml not in file_list:
                        logger.error("EPUB файл не содержит META-INF/container.xml")
                        return False
                    
                    # Проверяем наличие OPF файла
                    opf_files = [f for f in file_list if f.endswith('.opf')]
                    if not opf_files:
                        logger.warning("EPUB файл не содержит OPF файлов")
                    
                    # Проверяем наличие файлов с содержимым
                    content_files = self.get_content_files(epub_zip)
                    if not content_files:
                        logger.error("EPUB файл не содержит файлов с содержимым")
                        return False
                
            except zipfile.BadZipFile:
                logger.error("Файл не является валидным ZIP архивом")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка валидации EPUB файла {file_path}: {e}")
            return False


# Глобальный экземпляр парсера
epub_parser = EPUBParser()


def parse_epub_file(file_path: str) -> Dict[str, Any]:
    """Функция-обертка для парсинга EPUB файла"""
    return epub_parser.parse_file(file_path)


def validate_epub_file(file_path: str) -> bool:
    """Функция-обертка для валидации EPUB файла"""
    return epub_parser.validate_file(file_path)
