"""
Модели для структурированного представления контента
Единый формат для всех парсеров
"""

from enum import Enum
from typing import List, Optional, Dict, Any, Union
from dataclasses import dataclass
from pathlib import Path


class ContentType(Enum):
    """Типы элементов контента"""
    DIALOGUE = "dialogue"              # Диалог персонажа
    NARRATIVE = "narrative"            # Описательный текст, авторский текст
    CHARACTER_LIST = "character_list"  # Список персонажей/действующих лиц
    STAGE_DIRECTION = "stage_direction" # Сценические ремарки, указания
    CHAPTER_TITLE = "chapter_title"    # Заголовки глав, актов, действий
    SECTION_BREAK = "section_break"    # Разделители секций
    METADATA_BLOCK = "metadata_block"  # Блоки метаданных (автор, год и т.д.)


@dataclass
class ContentElement:
    """Элемент структурированного контента"""
    type: ContentType
    content: str
    position: int  # Позиция начала в оригинальном тексте
    length: int    # Длина элемента
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class DialogueElement(ContentElement):
    """Специализированный элемент для диалогов"""
    speaker: Optional[str] = None
    speaker_normalized: Optional[str] = None  # Нормализованное имя говорящего
    confidence: float = 1.0  # Уверенность в атрибуции
    
    def __post_init__(self):
        super().__post_init__()
        self.type = ContentType.DIALOGUE
        if self.speaker and not self.speaker_normalized:
            self.speaker_normalized = self._normalize_speaker_name(self.speaker)
        
        # Добавляем данные в metadata
        self.metadata.update({
            'speaker': self.speaker,
            'speaker_normalized': self.speaker_normalized,
            'confidence': self.confidence
        })
    
    def _normalize_speaker_name(self, name: str) -> str:
        """Нормализация имени говорящего"""
        if not name:
            return ""
        
        # Убираем лишние пробелы
        normalized = ' '.join(name.split())
        
        # Убираем знаки препинания в конце
        normalized = normalized.rstrip('.,!?:;')
        
        return normalized


@dataclass
class CharacterListElement(ContentElement):
    """Специализированный элемент для списка персонажей"""
    characters: List[Dict[str, str]] = None  # Список найденных персонажей
    
    def __post_init__(self):
        super().__post_init__()
        self.type = ContentType.CHARACTER_LIST
        if self.characters is None:
            self.characters = []
        
        self.metadata['characters'] = self.characters


@dataclass
class StructuredContent:
    """Структурированное представление контента файла"""
    elements: List[ContentElement]
    raw_content: str              # Оригинальный сырой текст
    metadata: Dict[str, Any]      # Метаданные файла
    source_file: Optional[str] = None
    
    def get_elements_by_type(self, content_type: ContentType) -> List[ContentElement]:
        """Получить все элементы определенного типа"""
        return [elem for elem in self.elements if elem.type == content_type]
    
    def get_dialogues(self) -> List[DialogueElement]:
        """Получить все диалоги"""
        return [elem for elem in self.elements if isinstance(elem, DialogueElement)]
    
    def get_character_lists(self) -> List[CharacterListElement]:
        """Получить все списки персонажей"""
        return [elem for elem in self.elements if isinstance(elem, CharacterListElement)]
    
    def get_speakers(self) -> List[str]:
        """Получить список всех говорящих в диалогах"""
        speakers = set()
        for dialogue in self.get_dialogues():
            if dialogue.speaker_normalized:
                speakers.add(dialogue.speaker_normalized)
        return sorted(list(speakers))
    
    def get_dialogue_count_by_speaker(self) -> Dict[str, int]:
        """Получить количество реплик по говорящим"""
        counts = {}
        for dialogue in self.get_dialogues():
            speaker = dialogue.speaker_normalized or "Unknown"
            counts[speaker] = counts.get(speaker, 0) + 1
        return counts
    
    def to_dict(self) -> Dict[str, Any]:
        """Конвертация в словарь для сериализации"""
        return {
            'elements': [
                {
                    'type': elem.type.value,
                    'content': elem.content,
                    'position': elem.position,
                    'length': elem.length,
                    'metadata': elem.metadata
                }
                for elem in self.elements
            ],
            'raw_content': self.raw_content,
            'metadata': self.metadata,
            'source_file': self.source_file,
            'statistics': {
                'total_elements': len(self.elements),
                'dialogues_count': len(self.get_dialogues()),
                'speakers_count': len(self.get_speakers()),
                'dialogue_distribution': self.get_dialogue_count_by_speaker()
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StructuredContent':
        """Создание объекта из словаря"""
        elements = []
        
        for elem_data in data.get('elements', []):
            content_type = ContentType(elem_data['type'])
            
            # Создаем специализированные элементы
            if content_type == ContentType.DIALOGUE:
                metadata = elem_data.get('metadata', {})
                element = DialogueElement(
                    content=elem_data['content'],
                    position=elem_data['position'],
                    length=elem_data['length'],
                    speaker=metadata.get('speaker'),
                    confidence=metadata.get('confidence', 1.0)
                )
            elif content_type == ContentType.CHARACTER_LIST:
                metadata = elem_data.get('metadata', {})
                element = CharacterListElement(
                    content=elem_data['content'],
                    position=elem_data['position'],
                    length=elem_data['length'],
                    characters=metadata.get('characters', [])
                )
            else:
                # Обычный элемент
                element = ContentElement(
                    type=content_type,
                    content=elem_data['content'],
                    position=elem_data['position'],
                    length=elem_data['length'],
                    metadata=elem_data.get('metadata', {})
                )
            
            elements.append(element)
        
        return cls(
            elements=elements,
            raw_content=data.get('raw_content', ''),
            metadata=data.get('metadata', {}),
            source_file=data.get('source_file')
        )


# Утилиты для работы с контентом
class ContentAnalyzer:
    """Анализатор структурированного контента"""
    
    @staticmethod
    def detect_dialogue_patterns(text: str) -> List[Dict[str, Any]]:
        """Поиск паттернов диалогов в тексте"""
        import re
        
        patterns = [
            # Формат: "ИМЯ: текст" или "ИМЯ. текст"
            r'^([А-ЯЁ][А-ЯЁа-яё\s]+?)[\.:]\s*(.+)$',
            # Формат: "— Текст, — сказал ИМЯ" 
            r'^—\s*(.+?),?\s*—\s*([а-яё]+(?:\s+[А-ЯЁ][а-яё]+)*)\.',
            # Формат с отступом: "    ИМЯ: текст"
            r'^\s+([А-ЯЁ][А-ЯЁа-яё\s]+?):\s*(.+)$'
        ]
        
        dialogues = []
        lines = text.split('\n')
        
        for line_num, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            for pattern in patterns:
                match = re.match(pattern, line, re.MULTILINE)
                if match:
                    if len(match.groups()) >= 2:
                        speaker = match.group(1).strip()
                        dialogue_text = match.group(2).strip()
                        
                        dialogues.append({
                            'speaker': speaker,
                            'text': dialogue_text,
                            'line_number': line_num,
                            'original_line': line
                        })
                        break
        
        return dialogues
    
    @staticmethod
    def detect_character_lists(text: str) -> List[Dict[str, Any]]:
        """Поиск списков персонажей в тексте"""
        import re
        
        # Паттерны заголовков секций персонажей
        section_patterns = [
            r'(?i)(действующие\s+лица)',
            r'(?i)(персонажи)',
            r'(?i)(лица)',
            r'(?i)(драматические\s+лица)'
        ]
        
        character_lists = []
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Ищем заголовки секций
            for pattern in section_patterns:
                if re.search(pattern, line):
                    # Найден заголовок, ищем персонажей после него
                    characters = []
                    j = i + 1
                    
                    while j < len(lines):
                        char_line = lines[j].strip()
                        if not char_line:
                            j += 1
                            continue
                        
                        # Проверяем, не началась ли новая секция
                        if re.search(r'(?i)(действие|акт|картина|сцена|явление)', char_line):
                            break
                        
                        # Пытаемся распарсить персонажа
                        char_match = re.match(r'^([А-ЯЁа-яё][А-ЯЁа-яё\s]+?)(?:[,—–-]\s*(.+?))?[\.]*$', char_line)
                        if char_match:
                            char_name = char_match.group(1).strip()
                            char_description = char_match.group(2).strip() if char_match.group(2) else ""
                            
                            characters.append({
                                'name': char_name,
                                'description': char_description,
                                'line_number': j
                            })
                        
                        j += 1
                    
                    if characters:
                        character_lists.append({
                            'section_title': line,
                            'characters': characters,
                            'start_line': i,
                            'end_line': j - 1
                        })
                    break
        
        return character_lists
