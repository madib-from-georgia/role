"""
Новый парсер чеклистов из JSON файлов для новой структуры данных
"""

import json
import hashlib
from typing import List, Dict, Any, Optional
from pathlib import Path
from loguru import logger


class ChecklistStructure:
    """Структура для хранения распарсенного чеклиста"""
    
    def __init__(self):
        self.external_id = ""  # id из JSON
        self.title = ""
        self.description = ""
        self.slug = ""
        self.icon = ""
        self.sections = []
        self.goal = ""  # Цель чеклиста
        self.file_hash = ""  # SHA-256 хеш файла
        self.version = "1.0.0"  # Версия


class ChecklistSection:
    """Секция чеклиста"""
    
    def __init__(self):
        self.external_id = ""  # id из JSON
        self.title = ""
        self.number = ""
        self.icon = ""
        self.order_index = 0
        self.subsections = []


class ChecklistSubsection:
    """Подсекция чеклиста"""
    
    def __init__(self):
        self.external_id = ""  # id из JSON
        self.title = ""
        self.number = ""
        self.order_index = 0
        self.question_groups = []
        self.examples = ""  # Примеры из литературы
        self.why_important = ""  # Почему это важно


class ChecklistQuestionGroup:
    """Группа вопросов"""
    
    def __init__(self):
        self.external_id = ""  # id из JSON
        self.title = ""
        self.order_index = 0
        self.questions = []


class ChecklistQuestion:
    """Отдельный вопрос"""
    
    def __init__(self):
        self.external_id = ""  # id из JSON
        self.text = ""
        self.order_index = 0
        self.answers = []  # Варианты ответов
        self.answer_type = "single"  # "single", "multiple"
        self.source_type = ""  # "text", "logic", "imagination"


class ChecklistAnswer:
    """Вариант ответа на вопрос"""
    
    def __init__(self):
        self.external_id = ""  # id из JSON
        self.value_male = ""
        self.value_female = ""
        self.exported_value_male = ""
        self.exported_value_female = ""
        self.hint = ""
        self.order_index = 0


class ChecklistJsonParserNew:
    """
    Новый парсер чеклистов из JSON файлов
    
    Ожидает JSON структуру согласно новой спецификации:
    {
        "id": "physical-portrait",
        "title": "Физический портрет",
        "sections": [
            {
                "id": "appearance",
                "title": "Внешность и физические данные",
                "subsections": [
                    {
                        "id": "physique",
                        "title": "Телосложение и антропометрия",
                        "questionGroups": [
                            {
                                "id": "height-proportions",
                                "title": "Рост и пропорции тела",
                                "questions": [
                                    {
                                        "id": "height",
                                        "title": "Какой у меня рост?",
                                        "answers": [
                                            {
                                                "id": "short",
                                                "value": {
                                                    "male": "низкий",
                                                    "female": "низкая"
                                                },
                                                "exportedValue": {
                                                    "male": "Я невысокого роста",
                                                    "female": "Я невысокого роста"
                                                },
                                                "hint": "Невысокий человек может компенсировать или комплексовать"
                                            }
                                        ],
                                        "answerType": "single",
                                        "source": "text"
                                    }
                                ]
                            }
                        ]
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
        logger.info(f"Парсинг JSON файла новой структуры: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                data = json.loads(content)
                
            # Вычисляем хеш файла
            file_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
            
        except Exception as e:
            raise ValueError(f"Ошибка чтения JSON файла: {e}")
        
        # Создаем структуру чеклиста
        structure = ChecklistStructure()
        
        # Заполняем основные поля
        structure.external_id = data.get('id', '')
        structure.title = data.get('title', '')
        structure.slug = self._generate_slug(structure.external_id)
        structure.file_hash = file_hash
        
        # Обрабатываем цель (если есть)
        goal_data = data.get('goal', {})
        if isinstance(goal_data, dict):
            structure.goal = goal_data.get('description', '')
        else:
            structure.goal = str(goal_data) if goal_data else ""
        
        # Обрабатываем секции
        sections_data = data.get('sections', [])
        for i, section_data in enumerate(sections_data):
            section = self._parse_section(section_data, i)
            structure.sections.append(section)
        
        logger.success(f"Успешно распарсен чеклист новой структуры: {structure.title}")
        return structure
    
    def parse_json_string(self, json_string: str) -> Dict[str, Any]:
        """
        Парсит JSON строку и возвращает словарь данных
        
        Args:
            json_string: JSON строка
            
        Returns:
            Словарь с данными чеклиста
        """
        try:
            data = json.loads(json_string)
            
            # Вычисляем хеш содержимого
            file_hash = hashlib.sha256(json_string.encode('utf-8')).hexdigest()
            
            # Добавляем хеш в данные
            data['file_hash'] = file_hash
            
            return data
            
        except Exception as e:
            raise ValueError(f"Ошибка парсинга JSON строки: {e}")
    
    def _parse_section(self, section_data: Dict[str, Any], order_index: int) -> ChecklistSection:
        """Парсит секцию"""
        section = ChecklistSection()
        section.external_id = section_data.get('id', '')
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
        subsection.external_id = subsection_data.get('id', '')
        subsection.title = subsection_data.get('title', '')
        subsection.order_index = order_index
        subsection.number = str(order_index + 1)
        
        # Обрабатываем группы вопросов
        groups_data = subsection_data.get('questionGroups', [])
        for i, group_data in enumerate(groups_data):
            group = self._parse_question_group(group_data, i)
            subsection.question_groups.append(group)
        
        # Обрабатываем примеры (если есть)
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
        
        # Обрабатываем важность (если есть)
        subsection.why_important = subsection_data.get('whyImportant', '')
        
        return subsection
    
    def _parse_question_group(self, group_data: Dict[str, Any], order_index: int) -> ChecklistQuestionGroup:
        """Парсит группу вопросов"""
        group = ChecklistQuestionGroup()
        group.external_id = group_data.get('id', '')
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
        question.external_id = question_data.get('id', '')
        question.text = question_data.get('title', '')
        question.order_index = order_index
        
        # Обрабатываем тип ответа
        question.answer_type = question_data.get('answerType', 'single')
        question.source_type = question_data.get('source', '')
        
        # Обрабатываем варианты ответов
        answers_data = question_data.get('answers', [])
        for i, answer_data in enumerate(answers_data):
            answer = self._parse_answer(answer_data, i)
            question.answers.append(answer)
        
        return question
    
    def _parse_answer(self, answer_data: Dict[str, Any], order_index: int) -> ChecklistAnswer:
        """Парсит вариант ответа"""
        answer = ChecklistAnswer()
        answer.external_id = answer_data.get('id', '')
        answer.order_index = order_index
        answer.hint = answer_data.get('hint', '')
        
        # Обрабатываем значения для разных полов
        value_data = answer_data.get('value', {})
        if isinstance(value_data, dict):
            answer.value_male = value_data.get('male', '')
            answer.value_female = value_data.get('female', '')
        else:
            # Если значение не разделено по полам, используем одинаковое
            answer.value_male = str(value_data)
            answer.value_female = str(value_data)
        
        # Обрабатываем экспортируемые значения
        exported_value_data = answer_data.get('exportedValue', {})
        if isinstance(exported_value_data, dict):
            answer.exported_value_male = exported_value_data.get('male', '')
            answer.exported_value_female = exported_value_data.get('female', '')
        else:
            # Если экспортируемое значение не разделено по полам
            answer.exported_value_male = str(exported_value_data) if exported_value_data else ""
            answer.exported_value_female = str(exported_value_data) if exported_value_data else ""
        
        return answer
    
    
    def _extract_icon(self, title: str) -> str:
        """Извлекает иконку из заголовка"""
        # Ищем эмодзи в начале заголовка
        import re
        emoji_match = re.match(r'^([^\w\s]+)', title.strip())
        if emoji_match:
            return emoji_match.group(1)
        return ""
    
    def _generate_slug(self, external_id: str) -> str:
        """Генерирует slug из external_id"""
        return external_id.lower().replace('_', '-')
    
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
        total_answers = sum(
            len(question.answers)
            for section in checklist.sections
            for subsection in section.subsections
            for group in subsection.question_groups
            for question in group.questions
        )
        
        return {
            "external_id": checklist.external_id,
            "title": checklist.title,
            "slug": checklist.slug,
            "file_hash": checklist.file_hash,
            "version": checklist.version,
            "total_sections": total_sections,
            "total_subsections": total_subsections,
            "total_groups": total_groups,
            "total_questions": total_questions,
            "total_answers": total_answers
        }