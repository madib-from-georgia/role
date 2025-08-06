"""
Парсер чеклистов из JSON файлов
"""

import json
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
        self.source = []  # Источники ответа: text, logic, imagination


class ChecklistJsonParser:
    """
    Парсер чеклистов из JSON файлов
    
    Ожидает JSON структуру:
    {
        "title": "Заголовок чеклиста",
        "goal": {
            "title": "Цель",
            "description": "Описание цели"
        },
        "sections": [
            {
                "title": "Заголовок секции",
                "subsections": [
                    {
                        "title": "Заголовок подсекции",
                        "groups": [
                            {
                                "title": "Заголовок группы",
                                "questions": [
                                    {
                                        "question": "Текст вопроса",
                                        "options": ["вариант1", "вариант2"],
                                        "optionsType": "single",
                                        "source": ["text", "logic"],
                                        "hint": "Подсказка"
                                    }
                                ]
                            }
                        ],
                        "examples": [
                            {
                                "text": "Пример из литературы",
                                "value": "Объяснение примера"
                            }
                        ],
                        "whyImportant": "Объяснение важности"
                    }
                ]
            }
        ]
    }
    """
    
    def __init__(self):
        pass
    
    def parse_file(self, file_path: str) -> ChecklistStructure:
        """
        Парсит JSON файл чеклиста
        
        Args:
            file_path: Путь к JSON файлу
            
        Returns:
            Структура чеклиста
        """
        logger.info(f"Парсинг JSON файла: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            raise ValueError(f"Ошибка чтения JSON файла: {e}")
        
        # Создаем структуру чеклиста
        structure = ChecklistStructure()
        
        # Заполняем основные поля
        structure.title = data.get('title', '')
        structure.slug = self._generate_slug(Path(file_path).stem)
        
        # Обрабатываем цель
        goal_data = data.get('goal', {})
        if isinstance(goal_data, dict):
            structure.goal = goal_data.get('description', '')
        else:
            structure.goal = str(goal_data)
        
        # Обрабатываем секции
        sections_data = data.get('sections', [])
        for i, section_data in enumerate(sections_data):
            section = self._parse_section(section_data, i)
            structure.sections.append(section)
        
        logger.success(f"Успешно распарсен чеклист: {structure.title}")
        return structure
    
    def _parse_section(self, section_data: Dict[str, Any], order_index: int) -> ChecklistSection:
        """Парсит секцию"""
        section = ChecklistSection()
        section.title = section_data.get('title', '')
        section.order_index = order_index
        section.number = str(order_index + 1)
        section.icon = self._extract_icon(section.title)
        
        # Обрабатываем подсекции
        subsections_data = section_data.get('subsections', [])
        for i, subsection_data in enumerate(subsections_data):
            subsection = self._parse_subsection(subsection_data, i)
            section.subsections.append(subsection)
        
        return section
    
    def _parse_subsection(self, subsection_data: Dict[str, Any], order_index: int) -> ChecklistSubsection:
        """Парсит подсекцию"""
        subsection = ChecklistSubsection()
        subsection.title = subsection_data.get('title', '')
        subsection.order_index = order_index
        subsection.number = str(order_index + 1)
        
        # Обрабатываем группы вопросов
        groups_data = subsection_data.get('groups', [])
        for i, group_data in enumerate(groups_data):
            group = self._parse_question_group(group_data, i)
            subsection.question_groups.append(group)
        
        # Обрабатываем примеры
        examples_data = subsection_data.get('examples', [])
        if examples_data:
            examples_text = []
            for example in examples_data:
                if isinstance(example, dict):
                    text = example.get('text', '')
                    value = example.get('value', '')
                    if text and value:
                        examples_text.append(f"{text}\n{value}")
                    elif text:
                        examples_text.append(text)
                else:
                    examples_text.append(str(example))
            subsection.examples = '\n\n'.join(examples_text)
        
        # Обрабатываем важность
        subsection.why_important = subsection_data.get('whyImportant', '')
        
        return subsection
    
    def _parse_question_group(self, group_data: Dict[str, Any], order_index: int) -> ChecklistQuestionGroup:
        """Парсит группу вопросов"""
        group = ChecklistQuestionGroup()
        group.title = group_data.get('title', '')
        group.order_index = order_index
        
        # Обрабатываем вопросы
        questions_data = group_data.get('questions', [])
        for i, question_data in enumerate(questions_data):
            question = self._parse_question(question_data, i)
            group.questions.append(question)
        
        return group
    
    def _parse_question(self, question_data: Dict[str, Any], order_index: int) -> ChecklistQuestion:
        """Парсит вопрос"""
        question = ChecklistQuestion()
        question.text = question_data.get('question', '')
        question.order_index = order_index
        question.hint = question_data.get('hint', '')
        
        # Обрабатываем варианты ответов
        options = question_data.get('options', [])
        question.options = options if isinstance(options, list) else []
        
        # Определяем тип вариантов
        options_type = question_data.get('optionsType', 'none')
        if options_type == 'single':
            question.option_type = 'single'
        elif options_type == 'multiple':
            question.option_type = 'multiple'
        else:
            question.option_type = 'none'
        
        # Обрабатываем источники
        source = question_data.get('source', [])
        question.source = source if isinstance(source, list) else []
        
        return question
    
    def _extract_icon(self, title: str) -> str:
        """Извлекает иконку из заголовка"""
        # Ищем эмодзи в начале заголовка
        import re
        emoji_match = re.match(r'^([^\w\s]+)', title.strip())
        if emoji_match:
            return emoji_match.group(1)
        return ""
    
    def _generate_slug(self, filename: str) -> str:
        """Генерирует slug из имени файла"""
        # Убираем префиксы и суффиксы
        slug = filename.replace('ACTOR_', '').replace('_CHECKLIST', '')
        # Заменяем подчеркивания на дефисы
        slug = slug.replace('_', '-').lower()
        return slug
    
    def get_structure_summary(self, checklist: ChecklistStructure) -> Dict[str, Any]:
        """
        Получает краткую сводку структуры чеклиста
        
        Args:
            checklist: Структура чеклиста
            
        Returns:
            Словарь с краткой информацией
        """
        total_sections = len(checklist.sections)
        total_subsections = sum(len(section.subsections) for section in checklist.sections)
        total_groups = sum(
            len(subsection.question_groups) 
            for section in checklist.sections 
            for subsection in section.subsections
        )
        total_questions = sum(
            len(group.questions)
            for section in checklist.sections
            for subsection in section.subsections
            for group in subsection.question_groups
        )
        
        return {
            "title": checklist.title,
            "slug": checklist.slug,
            "total_sections": total_sections,
            "total_subsections": total_subsections,
            "total_groups": total_groups,
            "total_questions": total_questions
        } 