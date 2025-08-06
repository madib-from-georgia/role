"""
Парсер чеклистов из Markdown файлов
"""

import re
from typing import List, Dict, Any, Optional
from pathlib import Path
from loguru import logger


class ChecklistStructure:
    """Структура для хранения распарсенного чеклиста"""
    
    def __init__(self):
        self.title = ""
        self.description = ""
        self.slug = ""
        self.icon = ""
        self.sections = []
        self.goal = ""  # Цель чеклиста
        self.how_to_use = ""  # Как использовать этот блок


class ChecklistSection:
    """Секция чеклиста"""
    
    def __init__(self):
        self.title = ""
        self.number = ""
        self.icon = ""
        self.order_index = 0
        self.subsections = []


class ChecklistSubsection:
    """Подсекция чеклиста"""
    
    def __init__(self):
        self.title = ""
        self.number = ""
        self.order_index = 0
        self.question_groups = []
        self.examples = ""  # Примеры из литературы
        self.why_important = ""  # Почему это важно


class ChecklistQuestionGroup:
    """Группа вопросов"""
    
    def __init__(self):
        self.title = ""
        self.order_index = 0
        self.questions = []


class ChecklistQuestion:
    """Отдельный вопрос"""
    
    def __init__(self):
        self.text = ""
        self.hint = ""
        self.order_index = 0
        self.options = []  # Варианты ответов
        self.option_type = "none"  # "single", "multiple", "none"


class ChecklistMarkdownParser:
    """
    Парсер чеклистов из Markdown файлов
    
    Парсит файлы в формате:
    # Заголовок чеклиста
    
    ## Цель чеклиста
    Текст цели чеклиста
    
    ## Как использовать этот блок
    Текст инструкции
    
    ## Опросник
    ### 📏 1. СЕКЦИЯ
    ### 1.1 Подсекция
    - Группа вопросов
      - [ ] **Вопрос**
        Варианты (один ответ): вариант1, вариант2, вариант3
        Варианты (много ответов): вариант1, вариант2, вариант3
        *Подсказка*
    
    ### Примеры из литературы
    Текст примеров
    
    ### Почему это важно
    Текст объяснения
    """
    
    def __init__(self):
        # Паттерны для парсинга
        self.title_pattern = r'^# (.+)$'
        self.goal_pattern = r'^## Цель чеклиста$'
        self.how_to_use_pattern = r'^## Как использовать этот блок$'
        self.survey_pattern = r'^## Опросник$'
        self.section_pattern = r'^## (.+)$'
        self.subsection_pattern = r'^### (.+)$'
        self.question_group_pattern = r'^- \*\*(.+)\*\*$'
        self.question_pattern = r'^\s*- \[ \] \*\*(.+?)\*\*'
        self.hint_pattern = r'^\s*\*(.+?)\*$'
        self.examples_pattern = r'^### Примеры из литературы$'
        self.why_important_pattern = r'^### Почему это важно$'
        
        # Паттерны для вариантов ответов
        self.single_options_pattern = r'^\s*Варианты \(один ответ\): (.+)$'
        self.multiple_options_pattern = r'^\s*Варианты \(много ответов\): (.+)$'
        
        # Альтернативные паттерны
        self.alt_question_group_pattern = r'^- (.+)$'
        self.alt_question_pattern = r'^\s+- \[ \] \*\*(.+?)\*\*'
        
        # Паттерны для подсказок (курсив)
        self.hint_italic_pattern = r'^\s*\*(.+?)\*$'
    
    def parse_file(self, file_path: str) -> ChecklistStructure:
        """
        Парсит Markdown файл чеклиста
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            Структура чеклиста
        """
        logger.info(f"Парсинг чеклиста: {file_path}")
        
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Файл не найден: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        checklist = ChecklistStructure()
        checklist.slug = self._generate_slug(file_path.stem)
        
        current_section = None
        current_subsection = None
        current_question_group = None
        last_question = None
        
        section_index = 0
        subsection_index = 0
        group_index = 0
        question_index = 0
        
        # Флаги для отслеживания текущего блока
        in_goal_block = False
        in_how_to_use_block = False
        in_survey_block = False
        in_examples_block = False
        in_why_important_block = False
        
        goal_lines = []
        how_to_use_lines = []
        examples_lines = []
        why_important_lines = []
        
        for line_num, line in enumerate(lines, 1):
            line = line.rstrip()
            
            if not line:
                continue
            
            # Заголовок чеклиста
            if match := re.match(self.title_pattern, line):
                title = match.group(1).strip()
                checklist.title = self._clean_title(title)
                checklist.icon = self._extract_icon(title)
                logger.debug(f"Найден заголовок: {checklist.title}")
                continue
            
            # Цель чеклиста
            if re.match(self.goal_pattern, line):
                in_goal_block = True
                in_how_to_use_block = False
                in_survey_block = False
                in_examples_block = False
                in_why_important_block = False
                goal_lines = []
                continue
            
            # Как использовать этот блок
            if re.match(self.how_to_use_pattern, line):
                in_goal_block = False
                in_how_to_use_block = True
                in_survey_block = False
                in_examples_block = False
                in_why_important_block = False
                how_to_use_lines = []
                continue
            
            # Опросник
            if re.match(self.survey_pattern, line):
                in_goal_block = False
                in_how_to_use_block = False
                in_survey_block = True
                in_examples_block = False
                in_why_important_block = False
                continue
            
            # Примеры из литературы
            if re.match(self.examples_pattern, line):
                in_goal_block = False
                in_how_to_use_block = False
                in_survey_block = False
                in_examples_block = True
                in_why_important_block = False
                examples_lines = []
                continue
            
            # Почему это важно
            if re.match(self.why_important_pattern, line):
                in_goal_block = False
                in_how_to_use_block = False
                in_survey_block = False
                in_examples_block = False
                in_why_important_block = True
                why_important_lines = []
                continue
            
            # Собираем текст для текстовых блоков
            if in_goal_block:
                goal_lines.append(line)
                continue
            
            if in_how_to_use_block:
                how_to_use_lines.append(line)
                continue
            
            if in_examples_block:
                examples_lines.append(line)
                continue
            
            if in_why_important_block:
                why_important_lines.append(line)
                continue
            
            # Секция (## заголовок) - только в опроснике
            if in_survey_block and (match := re.match(self.section_pattern, line)):
                title = match.group(1).strip()
                
                # Пропускаем специальные секции
                if title in ["Цель чеклиста", "Как использовать этот блок", "Опросник", "Примеры из литературы", "Почему это важно"]:
                    continue
                
                current_section = ChecklistSection()
                current_section.title = self._clean_title(title)
                current_section.icon = self._extract_icon(title)
                current_section.number = self._extract_number(title)
                current_section.order_index = section_index
                
                checklist.sections.append(current_section)
                section_index += 1
                subsection_index = 0
                
                logger.debug(f"Найдена секция: {current_section.title}")
                continue
            
            # Подсекция (### заголовок)
            if in_survey_block and (match := re.match(self.subsection_pattern, line)):
                if current_section is None:
                    # Создаем секцию по умолчанию
                    current_section = ChecklistSection()
                    current_section.title = "Основная секция"
                    current_section.order_index = section_index
                    checklist.sections.append(current_section)
                    section_index += 1
                    subsection_index = 0
                
                title = match.group(1).strip()
                
                # Пропускаем специальные подсекции
                if title in ["Примеры из литературы", "Почему это важно"]:
                    continue
                
                current_subsection = ChecklistSubsection()
                current_subsection.title = self._clean_title(title)
                current_subsection.number = self._extract_number(title)
                current_subsection.order_index = subsection_index
                
                current_section.subsections.append(current_subsection)
                subsection_index += 1
                group_index = 0
                
                logger.debug(f"Найдена подсекция: {current_subsection.title}")
                continue
            
            # Группа вопросов
            if in_survey_block and self._is_question_group(line):
                if current_subsection is None:
                    # Создаем подсекцию по умолчанию
                    if current_section is None:
                        current_section = ChecklistSection()
                        current_section.title = "Основная секция"
                        current_section.order_index = section_index
                        checklist.sections.append(current_section)
                        section_index += 1
                    
                    current_subsection = ChecklistSubsection()
                    current_subsection.title = "Основная подсекция"
                    current_subsection.order_index = subsection_index
                    current_section.subsections.append(current_subsection)
                    subsection_index += 1
                    group_index = 0
                
                title = self._extract_question_group_title(line)
                current_question_group = ChecklistQuestionGroup()
                current_question_group.title = title
                current_question_group.order_index = group_index
                
                current_subsection.question_groups.append(current_question_group)
                group_index += 1
                question_index = 0
                
                logger.debug(f"Найдена группа вопросов: {current_question_group.title}")
                continue
            
            # Вопрос
            if in_survey_block and (match := re.match(self.question_pattern, line)):
                if current_question_group is None:
                    # Создаем группу по умолчанию
                    if current_subsection is None:
                        if current_section is None:
                            current_section = ChecklistSection()
                            current_section.title = "Основная секция"
                            current_section.order_index = section_index
                            checklist.sections.append(current_section)
                            section_index += 1
                        
                        current_subsection = ChecklistSubsection()
                        current_subsection.title = "Основная подсекция"
                        current_subsection.order_index = subsection_index
                        current_section.subsections.append(current_subsection)
                        subsection_index += 1
                    
                    current_question_group = ChecklistQuestionGroup()
                    current_question_group.title = "Основные вопросы"
                    current_question_group.order_index = group_index
                    current_subsection.question_groups.append(current_question_group)
                    group_index += 1
                    question_index = 0
                
                question_text = match.group(1).strip()
                last_question = ChecklistQuestion()
                last_question.text = question_text
                last_question.order_index = question_index
                
                current_question_group.questions.append(last_question)
                question_index += 1
                
                logger.debug(f"Найден вопрос: {question_text[:50]}...")
                continue
            
            # Варианты ответов (один ответ)
            if in_survey_block and (match := re.match(self.single_options_pattern, line)):
                if last_question is not None:
                    options_text = match.group(1).strip()
                    options = [opt.strip() for opt in options_text.split(',')]
                    # Добавляем опцию "отвечу сам"
                    options.append("отвечу сам")
                    last_question.options = options
                    last_question.option_type = "single"
                    logger.debug(f"Найдены варианты (один): {options}")
                continue
            
            # Варианты ответов (много ответов)
            if in_survey_block and (match := re.match(self.multiple_options_pattern, line)):
                if last_question is not None:
                    options_text = match.group(1).strip()
                    options = [opt.strip() for opt in options_text.split(',')]
                    # Добавляем опцию "отвечу сам"
                    options.append("отвечу сам")
                    last_question.options = options
                    last_question.option_type = "multiple"
                    logger.debug(f"Найдены варианты (много): {options}")
                continue
            
            # Подсказка к вопросу (курсив)
            if in_survey_block and (match := re.match(self.hint_italic_pattern, line)):
                if last_question is not None:
                    hint_text = match.group(1).strip()
                    # Если подсказка уже есть, добавляем к ней
                    if last_question.hint:
                        last_question.hint += " " + hint_text
                    else:
                        last_question.hint = hint_text
                    logger.debug(f"Найдена подсказка: {hint_text[:50]}...")
                continue
        
        # Сохраняем текстовые блоки
        checklist.goal = '\n'.join(goal_lines).strip()
        checklist.how_to_use = '\n'.join(how_to_use_lines).strip()
        
        # Сохраняем примеры и объяснения для последней подсекции
        if current_subsection:
            current_subsection.examples = '\n'.join(examples_lines).strip()
            current_subsection.why_important = '\n'.join(why_important_lines).strip()
        
        logger.info(f"Парсинг завершен. Секций: {len(checklist.sections)}")
        return checklist
    
    def _is_question_group(self, line: str) -> bool:
        """Проверяет, является ли строка группой вопросов"""
        # Проверяем основные паттерны для групп вопросов
        if re.match(self.question_group_pattern, line):
            return True
        
        # Проверяем альтернативный паттерн
        if re.match(self.alt_question_group_pattern, line):
            # Убеждаемся, что это не вопрос
            if "- [ ]" not in line and line.strip().endswith("**"):
                return False
            # Проверяем, что это не список с подпунктами
            return not line.strip().startswith("- [ ]")
        
        return False
    
    def _extract_question_group_title(self, line: str) -> str:
        """Извлекает название группы вопросов"""
        # Пробуем основной паттерн
        if match := re.match(self.question_group_pattern, line):
            return match.group(1).strip()
        
        # Пробуем альтернативный паттерн
        if match := re.match(self.alt_question_group_pattern, line):
            title = match.group(1).strip()
            # Убираем жирное форматирование
            title = re.sub(r'\*\*(.+?)\*\*', r'\1', title)
            return title
        
        return line.strip().lstrip('- ').strip()
    
    def _clean_title(self, title: str) -> str:
        """Очищает заголовок от эмодзи и номеров"""
        # Убираем эмодзи в начале
        title = re.sub(r'^[^\w\s]+\s*', '', title)
        # Убираем номера типа "1." или "1.1" или просто "1"
        title = re.sub(r'^\d+(?:\.\d+)*\.?\s*', '', title)
        return title.strip()
    
    def _extract_icon(self, title: str) -> str:
        """Извлекает эмодзи/иконку из заголовка"""
        match = re.match(r'^([^\w\s]+)', title)
        return match.group(1).strip() if match else ""
    
    def _extract_number(self, title: str) -> str:
        """Извлекает номер из заголовка"""
        # Ищем номер после эмодзи
        match = re.search(r'(\d+(?:\.\d+)?)', title)
        return match.group(1) if match else ""
    
    def _generate_slug(self, filename: str) -> str:
        """Генерирует slug из имени файла"""
        # Убираем префиксы типа "ACTOR_"
        slug = filename.replace("ACTOR_", "")
        # Заменяем подчеркивания на дефисы и приводим к нижнему регистру
        slug = slug.replace("_", "-").lower()
        return slug
    
    def get_structure_summary(self, checklist: ChecklistStructure) -> Dict[str, Any]:
        """Получает краткую сводку структуры чеклиста"""
        total_questions = 0
        total_sections = len(checklist.sections)
        total_subsections = 0
        
        for section in checklist.sections:
            total_subsections += len(section.subsections)
            for subsection in section.subsections:
                for group in subsection.question_groups:
                    total_questions += len(group.questions)
        
        return {
            'title': checklist.title,
            'slug': checklist.slug,
            'sections_count': total_sections,
            'subsections_count': total_subsections,
            'questions_count': total_questions,
            'has_goal': bool(checklist.goal),
            'has_how_to_use': bool(checklist.how_to_use)
        }
