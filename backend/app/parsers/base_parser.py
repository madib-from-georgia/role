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
    
    def _normalize_play_content(self, raw_content: str) -> str:
        """
        Нормализация сырого контента пьесы для унифицированного формата.
        Приводит различные форматы пьес к единому стандарту.
        """
        import re
        
        if not raw_content:
            return ""
        
        # 1. Базовая очистка
        content = raw_content.strip()
        
        # 2. Удаляем лишние пустые строки (оставляем максимум 2 подряд)
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # 3. Нормализуем заголовки действий и явлений
        content = self._normalize_act_headers(content)
        
        # 4. Нормализуем диалоги к единому формату
        content = self._normalize_dialogue_format(content)
        
        # 5. Нормализуем списки персонажей
        content = self._normalize_character_lists(content)
        
        # 6. Нормализуем сценические ремарки
        content = self._normalize_stage_directions(content)
        
        # 7. Финальная очистка
        content = self._final_cleanup(content)
        
        return content

    def _normalize_act_headers(self, content: str) -> str:
        """Нормализация заголовков действий и явлений"""
        import re
        lines = content.split('\n')
        normalized_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                normalized_lines.append('')
                continue
                
            # Нормализуем заголовки действий
            if re.match(r'(?i)(действие|акт)\s*(первое|второе|третье|четвертое|пятое|\d+)', line):
                line = re.sub(r'\s+', ' ', line).title()
            
            # Нормализуем заголовки явлений
            elif re.match(r'(?i)(явление|сцена)\s*(первое|второе|третье|\d+)', line):
                line = re.sub(r'\s+', ' ', line).title()
            
            normalized_lines.append(line)
        
        return '\n'.join(normalized_lines)

    def _normalize_dialogue_format(self, content: str) -> str:
        """
        Приведение всех диалогов к единому формату: "ИМЯ: текст"
        """
        import re
        lines = content.split('\n')
        normalized_lines = []
        
        for line in lines:
            line = line.strip()
            
            if not line:
                normalized_lines.append('')
                continue
            
            # Паттерны различных форматов диалогов
            dialogue_patterns = [
                # "ИМЯ (действие). Текст" -> "ИМЯ (действие): Текст" (сохраняем действие в скобках)
                (r'^([А-ЯЁ][А-ЯЁа-яё\s]+?\s*\([^)]+\))\s*\.\s*(.+)$', r'\1: \2'),
                
                # "ИМЯ. Текст" -> "ИМЯ: Текст" (всегда ставим ровно один пробел)
                (r'^([А-ЯЁ][А-ЯЁа-яё\s]+?)\s*\.\s*(.+)$', r'\1: \2'),
                
                # "— Текст, — говорит ИМЯ." -> "ИМЯ: Текст"
                (r'^—\s*(.+?),?\s*—\s*([а-яё]+(?:\s+[А-ЯЁ][а-яё]+)*)\.$', r'\2: \1'),
                
                # Нормализуем уже существующие двоеточия (убираем лишние пробелы)
                (r'^([А-ЯЁ][А-ЯЁа-яё\s]+?)\s*:\s*(.+)$', r'\1: \2'),
            ]
            
            # Применяем паттерны
            for pattern, replacement in dialogue_patterns:
                if re.match(pattern, line):
                    line = re.sub(pattern, replacement, line)
                    break
            
            normalized_lines.append(line)
        
        return '\n'.join(normalized_lines)

    def _normalize_character_lists(self, content: str) -> str:
        """Нормализация списков персонажей"""
        import re
        lines = content.split('\n')
        normalized_lines = []
        in_character_list = False
        
        for line in lines:
            line = line.strip()
            
            # Определяем начало списка персонажей
            if re.search(r'(?i)(действующие\s+лица|персонажи|лица|драматические\s+лица)', line):
                in_character_list = True
                line = "ДЕЙСТВУЮЩИЕ ЛИЦА:"
                normalized_lines.append('')
                normalized_lines.append(line)
                normalized_lines.append('')
                continue
            
            # Определяем конец списка персонажей
            if in_character_list and (
                re.search(r'(?i)(действие|акт|явление|сцена)', line) or
                line.startswith('Действие происходит')
            ):
                in_character_list = False
                normalized_lines.append('')
            
            # Нормализуем строки персонажей
            if in_character_list and line:
                # Убираем лишние пробелы и точки в конце
                line = re.sub(r'\s+', ' ', line).rstrip('.')
                
            normalized_lines.append(line)
        
        return '\n'.join(normalized_lines)

    def _normalize_stage_directions(self, content: str) -> str:
        """Нормализация сценических ремарок"""
        import re
        lines = content.split('\n')
        normalized_lines = []
        
        for line in lines:
            original_line = line.strip()
            
            if not original_line:
                normalized_lines.append('')
                continue
            
            # Нормализуем ремарки в скобках
            if original_line.startswith('(') and original_line.endswith(')'):
                # Убираем лишние пробелы внутри скобок
                inside = original_line[1:-1].strip()
                line = f"({inside})"
            
            # Нормализуем отдельные ремарки (Пауза, Входит, etc.)
            elif re.match(r'(?i)^(пауза|входит|выходит|садится|встает|молчание)\.?$', original_line):
                line = original_line.rstrip('.').title() + '.'
            
            else:
                line = original_line
                
            normalized_lines.append(line)
        
        return '\n'.join(normalized_lines)

    def _final_cleanup(self, content: str) -> str:
        """Финальная очистка контента"""
        import re
        # Убираем множественные пустые строки
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # Убираем пробелы в начале и конце строк
        lines = content.split('\n')
        lines = [line.rstrip() for line in lines]
        
        # Убираем пустые строки в начале и конце
        while lines and not lines[0]:
            lines.pop(0)
        while lines and not lines[-1]:
            lines.pop()
        
        return '\n'.join(lines)
    
    def _save_normalization_debug_files(self, raw_content: str, normalized_content: str, file_path: str):
        """Временная функция для сохранения контента до и после нормализации"""
        import os
        from pathlib import Path
        from datetime import datetime
        
        print(f"================Сохраняем файлы отладки нормализации для: {file_path}")
        # Получаем имя файла без расширения и пути
        file_name = Path(file_path).stem
        
        # Создаем папку для логов этого файла
        logs_dir = Path(__file__).parent.parent.parent / "logs" / file_name
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Временная метка
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Сохраняем исходный контент
        raw_file = logs_dir / f"01_raw_content_{timestamp}.txt"
        with open(raw_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("ИСХОДНЫЙ КОНТЕНТ (ДО НОРМАЛИЗАЦИИ)\n")
            f.write("=" * 80 + "\n\n")
            f.write(raw_content)
        
        # Сохраняем нормализованный контент
        normalized_file = logs_dir / f"02_normalized_content_{timestamp}.txt"
        with open(normalized_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("НОРМАЛИЗОВАННЫЙ КОНТЕНТ (ПОСЛЕ НОРМАЛИЗАЦИИ)\n")
            f.write("=" * 80 + "\n\n")
            f.write(normalized_content)
        
        # Создаем файл сравнения
        comparison_file = logs_dir / f"03_comparison_{timestamp}.txt"
        with open(comparison_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("СРАВНЕНИЕ: ДО И ПОСЛЕ НОРМАЛИЗАЦИИ\n")
            f.write("=" * 80 + "\n\n")
            
            f.write("📊 СТАТИСТИКА:\n")
            f.write(f"   Исходная длина: {len(raw_content)} символов\n")
            f.write(f"   Нормализованная длина: {len(normalized_content)} символов\n")
            f.write(f"   Разница: {len(normalized_content) - len(raw_content)} символов\n")
            raw_lines_count = len(raw_content.split('\n'))
            norm_lines_count = len(normalized_content.split('\n'))
            f.write(f"   Исходных строк: {raw_lines_count}\n")
            f.write(f"   Нормализованных строк: {norm_lines_count}\n\n")
            
            f.write("🔍 ПЕРВЫЕ 50 СТРОК - СРАВНЕНИЕ:\n")
            f.write("-" * 80 + "\n")
            
            raw_lines = raw_content.split('\n')
            norm_lines = normalized_content.split('\n')
            
            max_lines = min(50, max(len(raw_lines), len(norm_lines)))
            
            for i in range(max_lines):
                f.write(f"Строка {i+1:3d}:\n")
                
                if i < len(raw_lines):
                    f.write(f"  ДО:    '{raw_lines[i]}'\n")
                else:
                    f.write(f"  ДО:    [отсутствует]\n")
                
                if i < len(norm_lines):
                    f.write(f"  ПОСЛЕ: '{norm_lines[i]}'\n")
                else:
                    f.write(f"  ПОСЛЕ: [отсутствует]\n")
                
                f.write("\n")
        
        print(f"🗂️ Файлы отладки нормализации сохранены в: {logs_dir}")
        print(f"   📄 Исходный: {raw_file.name}")
        print(f"   📄 Нормализованный: {normalized_file.name}")
        print(f"   📄 Сравнение: {comparison_file.name}")
    
    def _cleanup_normalization_debug_files(self, file_path: str):
        """Временная функция для очистки файлов отладки нормализации"""
        import shutil
        from pathlib import Path
        
        file_name = Path(file_path).stem
        logs_dir = Path(__file__).parent.parent.parent / "logs" / file_name
        
        if logs_dir.exists():
            # Удаляем только файлы нормализации (начинающиеся с 01_, 02_, 03_)
            for file in logs_dir.glob("0[123]_*content*.txt"):
                file.unlink()
            for file in logs_dir.glob("03_comparison*.txt"):
                file.unlink()
            print(f"🧹 Файлы отладки нормализации удалены из: {logs_dir}")
        else:
            print(f"⚠️ Папка логов не найдена: {logs_dir}")
    
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
        
        # НОРМАЛИЗАЦИЯ КОНТЕНТА ПЕРЕД АНАЛИЗОМ
        normalized_content = self._normalize_play_content(raw_content)
        
        # ВРЕМЕННО: Сохраняем файлы отладки для проверки качества нормализации
        self._save_normalization_debug_files(raw_content, normalized_content, file_path)
        
        elements = []
        
        # Анализируем НОРМАЛИЗОВАННЫЙ текст на предмет диалогов
        dialogues = ContentAnalyzer.detect_dialogue_patterns(normalized_content)
        
        # Анализируем НОРМАЛИЗОВАННЫЙ текст на предмет списков персонажей
        character_lists = ContentAnalyzer.detect_character_lists(normalized_content)
        
        # Обрабатываем списки персонажей
        for char_list in character_lists:
            start_pos = self._get_text_position_by_line(normalized_content, char_list['start_line'])
            end_pos = self._get_text_position_by_line(normalized_content, char_list['end_line'])
            
            element = CharacterListElement(
                type=ContentType.CHARACTER_LIST,
                content=char_list['section_title'],
                position=start_pos,
                length=end_pos - start_pos,
                characters=char_list['characters']
            )
            elements.append(element)
        
        # Обрабатываем диалоги
        processed_lines = set()
        for dialogue in dialogues:
            line_pos = self._get_text_position_by_line(normalized_content, dialogue['line_number'])
            
            element = DialogueElement(
                type=ContentType.DIALOGUE,
                content=dialogue['text'],
                position=line_pos,
                length=len(dialogue['original_line']),
                speaker=dialogue['speaker']
            )
            elements.append(element)
            processed_lines.add(dialogue['line_number'])
        
        # Обрабатываем оставшийся текст как нарративный
        lines = normalized_content.split('\n')
        for i, line in enumerate(lines):
            if i not in processed_lines and line.strip():
                # Проверяем, не входит ли эта строка в список персонажей
                in_character_list = any(
                    char_list['start_line'] <= i <= char_list['end_line']
                    for char_list in character_lists
                )
                
                if not in_character_list:
                    line_pos = self._get_text_position_by_line(normalized_content, i)
                    
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
            raw_content=normalized_content,  # Сохраняем нормализованную версию
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
    
    def _detect_content_type(self, line: str):
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
