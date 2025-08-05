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
        
        # 4. Сначала обрабатываем ремарки и объединяем разорванные реплики
        content = self._normalize_stage_directions(content)
        
        # 5. Обрабатываем безымянные реплики (присваиваем предыдущему говорящему)
        content = self._assign_orphan_speeches(content)
        
        # 6. Потом нормализуем диалоги к единому формату
        content = self._normalize_dialogue_format(content)
        
        # 7. Нормализуем ремарки внутри реплик персонажей
        content = self._normalize_inline_stage_directions(content)
        
        # 8. Нормализуем списки персонажей
        content = self._normalize_character_lists(content)
        
        # 9. Финальная очистка
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
            
            # Заключаем ремарки в именах персонажей в [[]]
            line = self._normalize_speaker_stage_directions(line)
            
            normalized_lines.append(line)
        
        return '\n'.join(normalized_lines)
    
    def _normalize_speaker_stage_directions(self, line: str) -> str:
        """
        Заключает ремарки в именах персонажей в [[]]
        Например: "Марина (наливает стакан): текст" -> "Марина [[наливает стакан]]: текст"
        """
        import re
        
        # Паттерн для поиска ремарок в скобках в начале строки (имя персонажа)
        # Ищем "ИМЯ (ремарка): текст" и заменяем на "ИМЯ [[ремарка]]: текст"
        pattern = r'^([А-ЯЁ][А-ЯЁа-яё\s]*?)\s*\(([^)]+)\)\s*:\s*(.+)$'
        match = re.match(pattern, line)
        
        if match:
            speaker_name = match.group(1).strip()
            stage_direction = match.group(2).strip()
            speech_text = match.group(3).strip()
            
            # Формируем новую строку с ремаркой в [[]]
            return f"{speaker_name} [[{stage_direction}]]: {speech_text}"
        
        return line
    
    def _normalize_inline_stage_directions(self, content: str) -> str:
        """
        Нормализует ремарки внутри реплик персонажей
        Заменяет (действие) на [[действие]] в тексте реплик
        """
        import re
        lines = content.split('\n')
        normalized_lines = []
        
        for line in lines:
            original_line = line.strip()
            
            if not original_line:
                normalized_lines.append('')
                continue
            
            # Проверяем, является ли это репликой персонажа
            if self._is_character_line(original_line):
                # Заменяем ремарки в скобках внутри речи на [[]]
                normalized_line = self._replace_inline_parentheses(original_line)
                normalized_lines.append(normalized_line)
            else:
                normalized_lines.append(original_line)
        
        return '\n'.join(normalized_lines)
    
    def _replace_inline_parentheses(self, line: str) -> str:
        """
        Заменяет ремарки в скобках внутри реплики на [[]]
        Но НЕ трогает скобки в имени персонажа в начале строки
        """
        import re
        
        # Находим границу между именем персонажа и его речью
        # Берем все до первого двоеточия как имя персонажа
        match = re.match(r'^([^:]+?):\s*(.+)$', line)
        
        if match:
            speaker_part = match.group(1)  # Имя персонажа (уже может содержать [[]])
            speech_part = match.group(2)   # Речь персонажа
            
            # В речевой части заменяем (текст) на [[текст]]
            # Ищем скобки, которые содержат ремарки (обычно начинаются с заглавной буквы или содержат глаголы)
            def replace_stage_direction(match):
                content = match.group(1).strip()
                
                # Проверяем, похоже ли это на ремарку
                if self._looks_like_stage_direction(content):
                    return f"[[{content}]]"
                else:
                    # Оставляем обычные скобки как есть
                    return f"({content})"
            
            # Заменяем скобки в речевой части
            normalized_speech = re.sub(r'\(([^)]+)\)', replace_stage_direction, speech_part)
            
            # Также ищем действия персонажей в конце реплики (не в скобках)
            # Паттерн: "Имя глагол" в конце предложения
            action_pattern = r'\.?\s*([А-ЯЁ][а-яё\s]{1,25}\s+(тихо\s+|громко\s+|медленно\s+)?(наигрывает|играет|поет|настраивает|ходит|садится|встает|уходит|входит|выходит|берет|дает|пьет|смотрит|смеется|плачет|обнимает)[^.]*)\.$'
            
            match_action = re.search(action_pattern, normalized_speech)
            if match_action:
                action_text = match_action.group(1).strip()
                # Убираем действие из речи и делаем его отдельной ремаркой
                speech_without_action = re.sub(action_pattern, '.', normalized_speech).strip()
                if speech_without_action.endswith('..'):
                    speech_without_action = speech_without_action[:-1]  # убираем лишнюю точку
                
                return f"{speaker_part}: {speech_without_action}\n[[{action_text}]]"
            
            return f"{speaker_part}: {normalized_speech}"
        
        return line
    
    def _looks_like_stage_direction(self, text: str) -> bool:
        """
        Определяет, является ли текст в скобках ремаркой
        """
        import re
        
        # Типичные признаки ремарок - расширенный список
        stage_direction_patterns = [
            # Движения и позы
            r'[Зз]евает',
            r'[Вв]ходит',
            r'[Вв]ыходит', 
            r'[Сс]адится',
            r'[Вв]стает',
            r'[Уу]ходит',
            r'[Пп]оворачивается',
            r'[Нн]аклоняется',
            r'[Оо]глядывается',
            r'[Пп]одходит',
            r'[Оо]тходит',
            r'[Пп]ерестанет',
            r'[Пп]родолжает',
            
            # Действия с предметами
            r'[Бб]ерет',
            r'[Дд]ержит',
            r'[Оо]ткрывает',
            r'[Зз]акрывает',
            r'[Пп]ротягивает',
            r'[Пп]одает',
            r'[Сс]тавит',
            r'[Кк]ладет',
            r'[Нн]аливает',
            r'[Пп]ьет',
            r'[Ее]ст',
            r'[Чч]итает',
            r'[Пп]ишет',
            r'[Ии]щет',
            r'[Оо]сматривает',
            r'[Тт]рогает',
            r'[Дд]отрагивается',
            
            # Взгляды и жесты
            r'[Сс]мотрит',
            r'[Пп]оказывает',
            r'[Дд]елает',
            r'[Кк]ивает',
            r'[Кк]ачает\s+головой',
            r'[Пп]ожимает\s+плечами',
            r'[Оо]бнимает',
            r'[Цц]елует',
            r'[Пп]рижимает',
            r'[Дд]ержит\s+за\s+руку',
            
            # Речевые действия
            r'[Гг]оворит',
            r'[Кк]ричит',
            r'[Шш]епчет',
            r'[Вв]осклицает',
            r'[Оо]твечает',
            r'[Пп]еребивает',
            r'[Сс]меется',
            r'[Пп]лачет',
            r'[Вв]здыхает',
            
            # Музыкальные действия
            r'[Нн]аигрывает',
            r'[Ии]грает',
            r'[Пп]оет',
            r'[Нн]астраивает',
            
            # Эмоциональные состояния и наречия
            r'тихо|громко|быстро|медленно|нежно|грубо|сердито',
            r'с\s+(досадой|радостью|грустью|удивлением|гневом|улыбкой)',
            r'весело|печально|задумчиво|рассеянно|внимательно',
            r'в\s+(недоумении|ужасе|восторге|смущении|гневе|печали)',
            r'скрестив\s+руки',
            r'нагнув\s+голову',
            r'подбоченясь',
            
            # Указания места и направления
            r'в\s+сторону|за\s+сцен|из-за|глазами',
            r'к\s+(окну|двери|столу)|от\s+(окна|двери|стола)',
            r'направо|налево|вверх|вниз|туда|сюда',
            
            # Временные указания
            r'после\s+паузы|через\s+минуту|вдруг|внезапно',
            
            # Общие паттерны
            r'^[А-ЯЁ][а-яё]+\.$',  # Слово с точкой в конце
        ]
        
        for pattern in stage_direction_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        # Убираем ограничения по длине - ремарки могут быть любой длины
        # Полагаемся только на конкретные паттерны действий и эмоций
        return False
    
    def _assign_orphan_speeches(self, content: str) -> str:
        """
        Присваивает безымянные реплики предыдущему говорящему
        """
        import re
        lines = content.split('\n')
        normalized_lines = []
        last_speaker = None
        
        for line in lines:
            original_line = line
            line = line.strip()
            
            if not line:
                normalized_lines.append('')
                continue
            
            # СНАЧАЛА проверяем, является ли это ремаркой (приоритет выше!)
            if self._is_stage_direction_line(line):
                normalized_lines.append(line)
                continue
            
            # ПОТОМ проверяем, может ли это быть безымянной репликой
            if self._is_orphan_speech(line) and last_speaker:
                # Присваиваем предыдущему говорящему
                assigned_line = f"{last_speaker}: {line}"
                normalized_lines.append(assigned_line)
                continue
            
            # Проверяем, является ли это репликой с указанием персонажа
            if self._is_character_line(line):
                # Извлекаем имя говорящего (может быть с двоеточием или точкой, с [[]] или ())
                speaker_match = (
                    re.match(r'^([А-ЯЁ][А-ЯЁа-яё\s]*(?:\[\[[^\]]+\]\])?[А-ЯЁа-яё\s]*?):\s*(.+)$', line) or
                    re.match(r'^([А-ЯЁ][А-ЯЁа-яё\s]*(?:\([^)]+\))?[А-ЯЁа-яё\s]*?):\s*(.+)$', line) or
                    re.match(r'^([А-ЯЁ][А-ЯЁа-яё\s]*(?:\([^)]+\))?)\s*\.\s*(.+?)(?:\s*\[\[[^\]]+\]\])?$', line) or  # с [[]] в конце
                    re.match(r'^([А-ЯЁ][А-ЯЁа-яё\s]*(?:\([^)]+\))?)\s*\.\s*(.+)$', line)  # без [[]] в конце
                )
                if speaker_match:
                    speaker_part = speaker_match.group(1).strip()
                    # Очищаем от действий в скобках и [[]] для запоминания
                    clean_speaker = re.sub(r'\s*\([^)]+\)\s*', '', speaker_part)
                    clean_speaker = re.sub(r'\s*\[\[[^\]]+\]\]\s*', '', clean_speaker).strip()
                    last_speaker = clean_speaker
                
                normalized_lines.append(line)
                continue
            
            # Иначе оставляем как есть
            normalized_lines.append(line)
        
        return '\n'.join(normalized_lines)
    
    def _is_orphan_speech(self, line: str) -> bool:
        """Проверяет, является ли строка безымянной репликой"""
        import re
        
        # Односложные фразы с многоточием
        if re.match(r'^[А-ЯЁ][а-яё]{0,3}\.\.\.?\s*$', line):
            return True
        
        # Короткие фразы начинающиеся со строчной буквы
        if re.match(r'^[а-яё].{1,20}$', line):
            return True
        
        # Фразы с многоточием в конце
        if re.match(r'^[А-ЯЁ][а-яё\s]{1,30}\.\.\.?\s*$', line):
            return True
        
        # Восклицания и междометия
        if re.match(r'^[А-ЯЁ][а-яё]{0,6}[!\?\.]*\s*$', line):
            return True
        
        return False

    def _normalize_character_lists(self, content: str) -> str:
        """Нормализация списков персонажей"""
        import re
        lines = content.split('\n')
        normalized_lines = []
        in_character_list = False
        
        for line in lines:
            line = line.strip()
            
            # Определяем начало списка персонажей (только как отдельные заголовки, не в репликах)
            if (re.match(r'(?i)^\s*(действующие\s+лица|персонажи|драматические\s+лица)\s*:?\s*$', line) and 
                not self._is_character_line(line)):
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
        """
        Нормализация ремарок и объединение разорванных реплик
        """
        import re
        lines = content.split('\n')
        normalized_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            if not line:
                normalized_lines.append('')
                i += 1
                continue
            
            # Проверяем, является ли это началом реплики персонажа
            if self._is_character_line(line):
                # Начинаем обработку реплики персонажа
                character_speech = line
                i += 1
                
                # Собираем продолжение реплики, включая ремарки
                while i < len(lines):
                    next_line = lines[i].strip()
                    
                    # Пустая строка - продолжаем поиск
                    if not next_line:
                        i += 1
                        continue
                    
                    # Если это новая реплика персонажа - прекращаем
                    if self._is_character_line(next_line):
                        break
                    
                    # Если это ремарка - различаем короткие и длинные/авторские ремарки
                    if self._is_stage_direction_line(next_line):
                        # Короткие ремарки (типа "Пауза", "Входит") присоединяем к реплике
                        if self._is_short_stage_direction(next_line):
                            character_speech += f" [[{next_line}]]"
                            i += 1
                            continue
                        else:
                            # Длинные авторские ремарки оставляем отдельно
                            break
                    
                    # Если это продолжение речи - добавляем
                    if self._is_speech_continuation(next_line):
                        character_speech += f" {next_line}"
                        i += 1
                        continue
                    
                    # Иначе прекращаем
                    break
                
                normalized_lines.append(character_speech)
            else:
                # Обрабатываем отдельные ремарки
                if self._is_stage_direction_line(line):
                    # Авторские ремарки заключаем в [[]]
                    line = f"[[{line}]]"
                
                normalized_lines.append(line)
                i += 1
        
        return '\n'.join(normalized_lines)
    
    def _is_character_line(self, line: str) -> bool:
        """Проверяет, является ли строка репликой персонажа"""
        import re
        
        # Паттерн для реплики с двоеточием: "ИМЯ: текст", "ИМЯ (действие): текст", "ИМЯ [[действие]]: текст"
        if re.match(r'^[А-ЯЁ][А-ЯЁа-яё\s]*(?:\([^)]+\)|\[\[[^\]]+\]\])?[А-ЯЁа-яё\s]*:\s*.+', line):
            return True
        
        # Паттерн для реплики с точкой (исходный формат): "ИМЯ. текст" или "ИМЯ (действие). текст"
        match = re.match(r'^([А-ЯЁ][А-ЯЁа-яё\s]*(?:\([^)]+\))?)\s*\.\s*(.+)$', line)
        if match:
            speaker_part = match.group(1).strip()
            speech_part = match.group(2).strip()
            
            # ВАЖНО: Проверяем, не является ли это ремаркой с действиями персонажа
            # НО только если действие НЕ находится в скобках после имени персонажа
            
            # Проверяем специальный случай: "Имя (действие в скобках). Речь"
            # Это должно оставаться репликой персонажа
            if re.match(r'^[А-ЯЁ][а-яё\s]*\s*\([^)]+\)\s*\.\s*.+', line):
                return True  # Это реплика персонажа с ремаркой в скобках
            
            action_verbs = [
                'настраивает', 'играет', 'поет', 'танцует', 'ходит', 'идет', 'бегает',
                'садится', 'встает', 'ложится', 'уходит', 'входит', 'выходит',
                'берет', 'дает', 'пьет', 'ест', 'читает', 'пишет', 'смотрит',
                'кричит', 'шепчет', 'плачет', 'смеется', 'молчит', 'кличет'
            ]
            
            # Проверяем, содержится ли глагол действия ВНЕ скобок
            # Убираем содержимое скобок и проверяем оставшийся текст
            text_without_parentheses = re.sub(r'\([^)]*\)', '', line).lower()
            for verb in action_verbs:
                # ВАЖНО: Ищем полные слова, а не подстроки (избегаем "дает" в "пообедаете")
                if re.search(r'\b' + verb + r'\b', text_without_parentheses):
                    return False  # Это ремарка, а не реплика
            
            # Если часть с говорящим содержит несколько слов или скобки - это реплика персонажа
            if (' ' in speaker_part or '(' in speaker_part or 
                len(speaker_part) > 4):  # Длинные имена - точно персонажи
                return True
            
            # Если речевая часть содержит не только короткое слово с многоточием - это реплика персонажа
            if not re.match(r'^[А-ЯЁ][а-яё]{0,2}\.\.\.?\s*$', speech_part):
                return True
            
        return False
    
    def _is_stage_direction_line(self, line: str) -> bool:
        """Проверяет, является ли строка ремаркой"""
        import re
        
        # ВАЖНО: Если строка начинается с имени персонажа, то это НЕ ремарка!
        if re.match(r'^[А-ЯЁ][А-ЯЁа-яё\s]*(?:\([^)]+\))?\s*[\.:]', line):
            return False
        
        # Типичные ремарки
        stage_direction_patterns = [
            r'^Пауза\.?$',
            r'^Молчание\.?$', 
            r'^Занавес\.?$',
            r'^Уходит\.?$',
            r'^Входит\s+.+\.?$',
            r'^Выходит\s+.+\.?$',
            r'^\([^)]+\)\.?$',  # Ремарки в скобках
            r'^[А-ЯЁ][а-яё]+\s+(за\s+сценой|в\s+дверях|из-за\s+кулис)',  # Ремарки с указанием места
            
            # Авторские ремарки, описывающие действие на сцене
            r'^Слышны?\s+(голоса|звуки|шаги)',  # "Слышны голоса", "Слышен звук"
            r'идут?\s+[А-ЯЁ]',  # "идут Серебряков, Елена Андреевна"
            r'входят?\s+[А-ЯЁ]',  # "входят персонажи"
            r'выходят?\s+[А-ЯЁ]',  # "выходят все"
            r'возвращаясь\s+с\s+прогулки',  # "возвращаясь с прогулки"
            r'из\s+глубины\s+(сада|леса|дома)',  # "из глубины сада"
            
            # Действия персонажей в ремарках (оптимизированные паттерны)
            r'^[А-ЯЁ][а-яё\s]{1,25}\s+(уходит|входит|выходит|садится|встает|ложится)\b',  # "Няня уходит", "Елена Андреевна уходит"
            r'^[А-ЯЁ][а-яё\s]{1,25}\s+(берет|дает|пьет|ест|читает|пишет|смотрит)\b',    # "Елена берет", "Елена Андреевна берет"  
            r'(уходит|входит|выходит|берет|дает|пьет|садится)\b.*,',  # Сложные ремарки с запятыми
            r'сидя\s+(на|в|у)\s+\w+',  # "сидя на качелях"
            r'стоя\s+(у|возле|около)\s+\w+',  # "стоя у окна"
            
            # Сложные многочастевые ремарки
            r'^[А-ЯЁ][а-яё\s]{1,25}\s+(играет|поет|настраивает|бьет)\s+[а-яё]+;',  # "Телегин играет польку;"
            r';.*все\s+(молча|тихо|внимательно)\s+(слушают|смотрят|ждут)',  # "; все молча слушают"
            r';.*входит\s+[а-яё]+',  # "; входит работник"
            r'^Оба\s+(уходят|идут|входят)',  # "Оба уходят в дом"
            r'^Все\s+(молча|тихо|внимательно)\s+(слушают|смотрят)',  # "Все молча слушают"
            r'[А-ЯЁ][а-яё\s]{1,25}\s+(ходит|идет|бегает)\s+(около|возле|по)\s+',  # "Марина ходит около дома"
            r'[а-яё]+\s+(кур|цыплят|кота|собаку)',  # "кличет кур", "зовет цыплят"
            r'настраивает\s+(гитару|инструмент|струны)',  # "настраивает гитару"
            r'что-то\s+(записывает|пишет|читает|делает)',  # "что-то записывает"
            r'\.\s*[А-ЯЁ][а-яё\s]{1,25}\s+(ходит|играет|настраивает|кличет)',  # ". Марина ходит около"
        ]
        
        for pattern in stage_direction_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                return True
        
        return False
    
    def _is_short_stage_direction(self, line: str) -> bool:
        """
        Проверяет, является ли ремарка короткой (для присоединения к реплике)
        или длинной авторской (для отдельной строки)
        """
        import re
        
        # Короткие ремарки - присоединяем к репликам
        short_patterns = [
            r'^Пауза\.?$',
            r'^Молчание\.?$', 
            r'^Занавес\.?$',
            r'^Уходит\.?$',
            r'^Входит\s+[А-ЯЁ][а-яё]+\.?$',  # Входит конкретный персонаж
            r'^Выходит\s+[А-ЯЁ][а-яё]+\.?$', # Выходит конкретный персонаж
            r'^\([^)]+\)\.?$',  # Ремарки в скобках
            r'^[А-ЯЁ][а-яё]+\s+(за\s+сценой|в\s+дверях|из-за\s+кулис)',
        ]
        
        for pattern in short_patterns:
            if re.match(pattern, line, re.IGNORECASE):
                return True
        
        # Если в строке есть перечисление персонажей через запятую - это авторская ремарка
        if ',' in line and re.search(r'[А-ЯЁ][а-яё]+.*,.*[А-ЯЁ][а-яё]+', line):
            return False
            
        # Если строка содержит точку с запятой - скорее всего сложная авторская ремарка
        if ';' in line:
            return False
            
        # Если строка длинная (более 50 символов) - скорее всего авторская ремарка
        if len(line) > 50:
            return False
            
        # Остальные ремарки считаем короткими
        return True
    
    def _is_speech_continuation(self, line: str) -> bool:
        """Проверяет, является ли строка продолжением речи персонажа"""
        import re
        
        # Продолжение речи - строка не является ремаркой
        if self._is_stage_direction_line(line):
            return False
        
        # Специальный случай: односложные фразы с многоточием - это продолжения речи
        if re.match(r'^[А-ЯЁ][а-яё]{0,2}\.\.\.?\s*$', line):
            return True
            
        # Если это полноценная реплика персонажа - не продолжение
        if self._is_character_line(line):
            return False
            
        # Если строка начинается с заглавной буквы, но это не имя персонажа
        # (например, начало предложения)
        if re.match(r'^[а-яё]', line):  # Строчная буква в начале - точно продолжение
            return True
            
        # Проверяем наличие знаков продолжения речи
        continuation_patterns = [
            r'^[А-ЯЁ][а-яё]+[,\.\!\?\s]',  # Обычное предложение
            r'^[А-ЯЁ][а-яё]*\s+[а-яё]',   # Обычное предложение с пробелом
            r'^\.\.\.',  # Многоточие в начале
            r'^—',       # Тире (продолжение диалога)
        ]
        
        for pattern in continuation_patterns:
            if re.match(pattern, line):
                return True
                
        return False
    
    def _normalize_single_stage_direction(self, line: str) -> str:
        """Нормализует отдельную ремарку"""
        import re
        
        # Нормализуем ремарки в скобках
        if line.startswith('(') and line.endswith(')'):
            # Убираем лишние пробелы внутри скобок
            inside = line[1:-1].strip()
            return f"({inside})"
        
        # Нормализуем отдельные ремарки (Пауза, Входит, etc.)
        elif re.match(r'(?i)^(пауза|входит|выходит|садится|встает|молчание)\.?$', line):
            return line.rstrip('.').title() + '.'
        
        return line

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
