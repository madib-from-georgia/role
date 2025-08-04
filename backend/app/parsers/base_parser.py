"""
Базовый класс для всех парсеров файлов.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from pathlib import Path
import logging

from .content_models import StructuredContent, ContentAnalyzer

logger = logging.getLogger(__name__)


class BaseParser(ABC):
    """Базовый класс для парсеров файлов."""
    
    def __init__(self):
        self.supported_extensions = []
        self.max_file_size = 50 * 1024 * 1024  # 50MB по умолчанию
    
    @abstractmethod
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """
        Парсинг файла (legacy метод для совместимости).
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            Словарь с контентом и метаданными
        """
        pass
    
    @abstractmethod
    def parse_to_structured_content(self, file_path: str) -> StructuredContent:
        """
        Парсинг файла в структурированный формат.
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            Объект StructuredContent с разобранным контентом
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
    
    def _create_structured_content_from_text(self, raw_content: str, metadata: Dict[str, Any], 
                                           file_path: str) -> StructuredContent:
        """
        Создание структурированного контента из сырого текста.
        Базовая реализация для простых текстов.
        """
        from .content_models import (
            ContentElement, DialogueElement, CharacterListElement,
            ContentType, StructuredContent
        )
        
        elements = []
        
        # Анализируем текст на предмет диалогов
        dialogues = ContentAnalyzer.detect_dialogue_patterns(raw_content)
        
        # Анализируем текст на предмет списков персонажей
        character_lists = ContentAnalyzer.detect_character_lists(raw_content)
        
        # Обрабатываем списки персонажей
        for char_list in character_lists:
            start_pos = self._get_text_position_by_line(raw_content, char_list['start_line'])
            end_pos = self._get_text_position_by_line(raw_content, char_list['end_line'])
            
            element = CharacterListElement(
                content=char_list['section_title'],
                position=start_pos,
                length=end_pos - start_pos,
                characters=char_list['characters']
            )
            elements.append(element)
        
        # Обрабатываем диалоги
        processed_lines = set()
        for dialogue in dialogues:
            line_pos = self._get_text_position_by_line(raw_content, dialogue['line_number'])
            
            element = DialogueElement(
                content=dialogue['text'],
                position=line_pos,
                length=len(dialogue['original_line']),
                speaker=dialogue['speaker']
            )
            elements.append(element)
            processed_lines.add(dialogue['line_number'])
        
        # Обрабатываем оставшийся текст как нарративный
        lines = raw_content.split('\n')
        for i, line in enumerate(lines):
            if i not in processed_lines and line.strip():
                # Проверяем, не входит ли эта строка в список персонажей
                in_character_list = any(
                    char_list['start_line'] <= i <= char_list['end_line']
                    for char_list in character_lists
                )
                
                if not in_character_list:
                    line_pos = self._get_text_position_by_line(raw_content, i)
                    
                    # Определяем тип контента
                    content_type = self._detect_content_type(line.strip())
                    
                    element = ContentElement(
                        type=content_type,
                        content=line.strip(),
                        position=line_pos,
                        length=len(line)
                    )
                    elements.append(element)
        
        # Сортируем элементы по позиции
        elements.sort(key=lambda x: x.position)
        
        return StructuredContent(
            elements=elements,
            raw_content=raw_content,
            metadata=metadata,
            source_file=file_path
        )
    
    def _get_text_position_by_line(self, text: str, line_number: int) -> int:
        """Получить позицию символа по номеру строки"""
        lines = text.split('\n')
        position = 0
        
        for i in range(min(line_number, len(lines))):
            if i > 0:
                position += 1  # Учитываем символ перевода строки
            position += len(lines[i])
        
        return position
    
    def _detect_content_type(self, line: str) -> 'ContentType':
        """Определение типа контента для строки"""
        import re
        from .content_models import ContentType
        
        line_lower = line.lower()
        
        # Заголовки действий/актов
        if re.search(r'\b(действие|акт|картина|сцена|явление|пролог|эпилог)\b', line_lower):
            return ContentType.CHAPTER_TITLE
        
        # Сценические ремарки (в скобках или курсиве)
        if (line.startswith('(') and line.endswith(')')) or \
           (line.startswith('[') and line.endswith(']')):
            return ContentType.STAGE_DIRECTION
        
        # По умолчанию - нарратив
        return ContentType.NARRATIVE
