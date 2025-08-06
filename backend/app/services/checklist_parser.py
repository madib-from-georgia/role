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


class ChecklistMarkdownParser:
    """
    Парсер чеклистов из Markdown файлов
    
    Парсит файлы в формате:
    # Заголовок чеклиста
    ## 📏 1. СЕКЦИЯ
    ### 1.1 Подсекция
    - Группа вопросов
      - [ ] **Вопрос**
        *Подсказка*
    """
    
    def __init__(self):
        # Паттерны для парсинга
        self.title_pattern = r'^# (.+)$'
        self.section_pattern = r'^## (.+)$'
        self.subsection_pattern = r'^### (.+)$'
        self.question_group_pattern = r'^- \*\*(.+)\*\*$'
        self.question_pattern = r'^\s*- \[ \] \*\*(.+?)\*\*'
        self.hint_pattern = r'^\s*\*(.+?)\*$'
        
        # Альтернативные паттерны
        self.alt_question_group_pattern = r'^- (.+)$'
        self.alt_question_pattern = r'^\s+- \[ \] \*\*(.+?)\*\*'
    
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
            
            # Секция (## заголовок)
            if match := re.match(self.section_pattern, line):
                title = match.group(1).strip()
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
            if match := re.match(self.subsection_pattern, line):
                if current_section is None:
                    logger.warning(f"Строка {line_num}: Подсекция без секции")
                    continue
                
                title = match.group(1).strip()
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
            if self._is_question_group(line):
                if current_subsection is None:
                    logger.warning(f"Строка {line_num}: Группа вопросов без подсекции")
                    continue
                
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
            if match := re.match(self.question_pattern, line):
                if current_question_group is None:
                    # Пытаемся создать группу по умолчанию
                    if current_subsection is not None:
                        current_question_group = ChecklistQuestionGroup()
                        current_question_group.title = "Основные вопросы"
                        current_question_group.order_index = group_index
                        current_subsection.question_groups.append(current_question_group)
                        group_index += 1
                    else:
                        logger.warning(f"Строка {line_num}: Вопрос без группы")
                        continue
                
                question_text = match.group(1).strip()
                last_question = ChecklistQuestion()
                last_question.text = question_text
                last_question.order_index = question_index
                
                current_question_group.questions.append(last_question)
                question_index += 1
                
                logger.debug(f"Найден вопрос: {question_text[:50]}...")
                continue
            
            # Подсказка к вопросу
            if match := re.match(self.hint_pattern, line):
                if last_question is not None:
                    hint_text = match.group(1).strip()
                    last_question.hint = hint_text
                    logger.debug(f"Найдена подсказка: {hint_text[:50]}...")
                continue
        
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
        """Возвращает краткую сводку структуры чеклиста"""
        total_questions = 0
        sections_summary = []
        
        for section in checklist.sections:
            section_questions = 0
            subsections_summary = []
            
            for subsection in section.subsections:
                subsection_questions = sum(len(group.questions) for group in subsection.question_groups)
                section_questions += subsection_questions
                
                subsections_summary.append({
                    "title": subsection.title,
                    "number": subsection.number,
                    "groups": len(subsection.question_groups),
                    "questions": subsection_questions
                })
            
            total_questions += section_questions
            sections_summary.append({
                "title": section.title,
                "number": section.number,
                "icon": section.icon,
                "subsections": len(section.subsections),
                "questions": section_questions,
                "subsections_detail": subsections_summary
            })
        
        return {
            "title": checklist.title,
            "slug": checklist.slug,
            "icon": checklist.icon,
            "total_sections": len(checklist.sections),
            "total_questions": total_questions,
            "sections": sections_summary
        }
