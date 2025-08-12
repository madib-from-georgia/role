"""
Сервис для сопоставления сущностей между версиями чеклистов
"""

from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from loguru import logger

from app.database.models.checklist import (
    Checklist, ChecklistSection, ChecklistSubsection,
    ChecklistQuestionGroup, ChecklistQuestion, ChecklistAnswer
)


class MatchType(str, Enum):
    """Типы сопоставления сущностей"""
    EXACT = "exact"           # Точное совпадение по external_id
    SIMILAR = "similar"       # Похожие сущности (по названию/тексту)
    NEW = "new"              # Новая сущность
    DELETED = "deleted"      # Удаленная сущность
    MOVED = "moved"          # Перемещенная сущность


@dataclass
class EntityMatch:
    """Результат сопоставления сущности"""
    old_entity: Optional[Any]
    new_entity: Optional[Any]
    match_type: MatchType
    confidence: float  # Уверенность в сопоставлении (0.0 - 1.0)
    reason: str       # Причина сопоставления
    external_id: Optional[str] = None


class EntityMatcher:
    """
    Сервис для сопоставления сущностей между версиями чеклистов
    
    Основные функции:
    - Сопоставление по external_id
    - Поиск похожих сущностей по содержимому
    - Определение перемещенных сущностей
    - Анализ изменений структуры
    """
    
    def __init__(self):
        self.similarity_threshold = 0.8  # Порог схожести для сопоставления
    
    def match_checklists(self, old_checklist: Checklist, new_structure) -> Dict[str, List[EntityMatch]]:
        """
        Сопоставляет все сущности между старой и новой версиями чеклиста
        
        Args:
            old_checklist: Существующий чеклист из БД
            new_structure: Новая структура из JSON
            
        Returns:
            Словарь с результатами сопоставления по типам сущностей
        """
        logger.info(f"Сопоставление сущностей для чеклиста: {old_checklist.external_id}")
        
        results = {
            "sections": [],
            "subsections": [],
            "question_groups": [],
            "questions": [],
            "answers": []
        }
        
        # Сопоставляем секции
        results["sections"] = self.match_sections(old_checklist.sections, new_structure.sections)
        
        # Сопоставляем подсекции
        old_subsections = []
        new_subsections = []
        for section in old_checklist.sections:
            old_subsections.extend(section.subsections)
        for section in new_structure.sections:
            new_subsections.extend(section.subsections)
        
        results["subsections"] = self.match_subsections(old_subsections, new_subsections)
        
        # Сопоставляем группы вопросов
        old_groups = []
        new_groups = []
        for subsection in old_subsections:
            old_groups.extend(subsection.question_groups)
        for subsection in new_subsections:
            new_groups.extend(subsection.question_groups)
        
        results["question_groups"] = self.match_question_groups(old_groups, new_groups)
        
        # Сопоставляем вопросы
        old_questions = []
        new_questions = []
        for group in old_groups:
            old_questions.extend(group.questions)
        for group in new_groups:
            new_questions.extend(group.questions)
        
        results["questions"] = self.match_questions(old_questions, new_questions)
        
        # Сопоставляем ответы
        old_answers = []
        new_answers = []
        for question in old_questions:
            old_answers.extend(question.answers)
        for question in new_questions:
            new_answers.extend(question.answers)
        
        results["answers"] = self.match_answers(old_answers, new_answers)
        
        return results
    
    def match_sections(self, old_sections: List[ChecklistSection], new_sections: List) -> List[EntityMatch]:
        """Сопоставляет секции чеклиста"""
        matches = []
        
        # Создаем индексы для быстрого поиска
        old_by_id = {s.external_id: s for s in old_sections}
        new_by_id = {s.external_id: s for s in new_sections}
        
        matched_old = set()
        matched_new = set()
        
        # 1. Точные совпадения по external_id
        for external_id in old_by_id.keys() & new_by_id.keys():
            old_section = old_by_id[external_id]
            new_section = new_by_id[external_id]
            
            matches.append(EntityMatch(
                old_entity=old_section,
                new_entity=new_section,
                match_type=MatchType.EXACT,
                confidence=1.0,
                reason="Точное совпадение по external_id",
                external_id=external_id
            ))
            
            matched_old.add(external_id)
            matched_new.add(external_id)
        
        # 2. Поиск похожих секций
        unmatched_old = [s for s in old_sections if s.external_id not in matched_old]
        unmatched_new = [s for s in new_sections if s.external_id not in matched_new]
        
        for old_section in unmatched_old:
            best_match = None
            best_confidence = 0.0
            
            for new_section in unmatched_new:
                if new_section.external_id in matched_new:
                    continue
                
                confidence = self._calculate_section_similarity(old_section, new_section)
                if confidence > best_confidence and confidence >= self.similarity_threshold:
                    best_match = new_section
                    best_confidence = confidence
            
            if best_match:
                matches.append(EntityMatch(
                    old_entity=old_section,
                    new_entity=best_match,
                    match_type=MatchType.SIMILAR,
                    confidence=best_confidence,
                    reason=f"Похожие секции (уверенность: {best_confidence:.2f})",
                    external_id=best_match.external_id
                ))
                matched_new.add(best_match.external_id)
            else:
                # Секция удалена
                matches.append(EntityMatch(
                    old_entity=old_section,
                    new_entity=None,
                    match_type=MatchType.DELETED,
                    confidence=1.0,
                    reason="Секция удалена в новой версии",
                    external_id=old_section.external_id
                ))
        
        # 3. Новые секции
        for new_section in unmatched_new:
            if new_section.external_id not in matched_new:
                matches.append(EntityMatch(
                    old_entity=None,
                    new_entity=new_section,
                    match_type=MatchType.NEW,
                    confidence=1.0,
                    reason="Новая секция в обновленной версии",
                    external_id=new_section.external_id
                ))
        
        return matches
    
    def match_subsections(self, old_subsections: List[ChecklistSubsection], new_subsections: List) -> List[EntityMatch]:
        """Сопоставляет подсекции чеклиста"""
        matches = []
        
        old_by_id = {s.external_id: s for s in old_subsections}
        new_by_id = {s.external_id: s for s in new_subsections}
        
        matched_old = set()
        matched_new = set()
        
        # Точные совпадения
        for external_id in old_by_id.keys() & new_by_id.keys():
            old_subsection = old_by_id[external_id]
            new_subsection = new_by_id[external_id]
            
            matches.append(EntityMatch(
                old_entity=old_subsection,
                new_entity=new_subsection,
                match_type=MatchType.EXACT,
                confidence=1.0,
                reason="Точное совпадение по external_id",
                external_id=external_id
            ))
            
            matched_old.add(external_id)
            matched_new.add(external_id)
        
        # Похожие подсекции
        unmatched_old = [s for s in old_subsections if s.external_id not in matched_old]
        unmatched_new = [s for s in new_subsections if s.external_id not in matched_new]
        
        for old_subsection in unmatched_old:
            best_match = None
            best_confidence = 0.0
            
            for new_subsection in unmatched_new:
                if new_subsection.external_id in matched_new:
                    continue
                
                confidence = self._calculate_subsection_similarity(old_subsection, new_subsection)
                if confidence > best_confidence and confidence >= self.similarity_threshold:
                    best_match = new_subsection
                    best_confidence = confidence
            
            if best_match:
                matches.append(EntityMatch(
                    old_entity=old_subsection,
                    new_entity=best_match,
                    match_type=MatchType.SIMILAR,
                    confidence=best_confidence,
                    reason=f"Похожие подсекции (уверенность: {best_confidence:.2f})",
                    external_id=best_match.external_id
                ))
                matched_new.add(best_match.external_id)
            else:
                matches.append(EntityMatch(
                    old_entity=old_subsection,
                    new_entity=None,
                    match_type=MatchType.DELETED,
                    confidence=1.0,
                    reason="Подсекция удалена",
                    external_id=old_subsection.external_id
                ))
        
        # Новые подсекции
        for new_subsection in unmatched_new:
            if new_subsection.external_id not in matched_new:
                matches.append(EntityMatch(
                    old_entity=None,
                    new_entity=new_subsection,
                    match_type=MatchType.NEW,
                    confidence=1.0,
                    reason="Новая подсекция",
                    external_id=new_subsection.external_id
                ))
        
        return matches
    
    def match_question_groups(self, old_groups: List[ChecklistQuestionGroup], new_groups: List) -> List[EntityMatch]:
        """Сопоставляет группы вопросов"""
        matches = []
        
        old_by_id = {g.external_id: g for g in old_groups}
        new_by_id = {g.external_id: g for g in new_groups}
        
        matched_old = set()
        matched_new = set()
        
        # Точные совпадения
        for external_id in old_by_id.keys() & new_by_id.keys():
            old_group = old_by_id[external_id]
            new_group = new_by_id[external_id]
            
            matches.append(EntityMatch(
                old_entity=old_group,
                new_entity=new_group,
                match_type=MatchType.EXACT,
                confidence=1.0,
                reason="Точное совпадение по external_id",
                external_id=external_id
            ))
            
            matched_old.add(external_id)
            matched_new.add(external_id)
        
        # Похожие группы
        unmatched_old = [g for g in old_groups if g.external_id not in matched_old]
        unmatched_new = [g for g in new_groups if g.external_id not in matched_new]
        
        for old_group in unmatched_old:
            best_match = None
            best_confidence = 0.0
            
            for new_group in unmatched_new:
                if new_group.external_id in matched_new:
                    continue
                
                confidence = self._calculate_group_similarity(old_group, new_group)
                if confidence > best_confidence and confidence >= self.similarity_threshold:
                    best_match = new_group
                    best_confidence = confidence
            
            if best_match:
                matches.append(EntityMatch(
                    old_entity=old_group,
                    new_entity=best_match,
                    match_type=MatchType.SIMILAR,
                    confidence=best_confidence,
                    reason=f"Похожие группы (уверенность: {best_confidence:.2f})",
                    external_id=best_match.external_id
                ))
                matched_new.add(best_match.external_id)
            else:
                matches.append(EntityMatch(
                    old_entity=old_group,
                    new_entity=None,
                    match_type=MatchType.DELETED,
                    confidence=1.0,
                    reason="Группа удалена",
                    external_id=old_group.external_id
                ))
        
        # Новые группы
        for new_group in unmatched_new:
            if new_group.external_id not in matched_new:
                matches.append(EntityMatch(
                    old_entity=None,
                    new_entity=new_group,
                    match_type=MatchType.NEW,
                    confidence=1.0,
                    reason="Новая группа",
                    external_id=new_group.external_id
                ))
        
        return matches
    
    def match_questions(self, old_questions: List[ChecklistQuestion], new_questions: List) -> List[EntityMatch]:
        """Сопоставляет вопросы"""
        matches = []
        
        old_by_id = {q.external_id: q for q in old_questions}
        new_by_id = {q.external_id: q for q in new_questions}
        
        matched_old = set()
        matched_new = set()
        
        # Точные совпадения
        for external_id in old_by_id.keys() & new_by_id.keys():
            old_question = old_by_id[external_id]
            new_question = new_by_id[external_id]
            
            matches.append(EntityMatch(
                old_entity=old_question,
                new_entity=new_question,
                match_type=MatchType.EXACT,
                confidence=1.0,
                reason="Точное совпадение по external_id",
                external_id=external_id
            ))
            
            matched_old.add(external_id)
            matched_new.add(external_id)
        
        # Похожие вопросы
        unmatched_old = [q for q in old_questions if q.external_id not in matched_old]
        unmatched_new = [q for q in new_questions if q.external_id not in matched_new]
        
        for old_question in unmatched_old:
            best_match = None
            best_confidence = 0.0
            
            for new_question in unmatched_new:
                if new_question.external_id in matched_new:
                    continue
                
                confidence = self._calculate_question_similarity(old_question, new_question)
                if confidence > best_confidence and confidence >= self.similarity_threshold:
                    best_match = new_question
                    best_confidence = confidence
            
            if best_match:
                matches.append(EntityMatch(
                    old_entity=old_question,
                    new_entity=best_match,
                    match_type=MatchType.SIMILAR,
                    confidence=best_confidence,
                    reason=f"Похожие вопросы (уверенность: {best_confidence:.2f})",
                    external_id=best_match.external_id
                ))
                matched_new.add(best_match.external_id)
            else:
                matches.append(EntityMatch(
                    old_entity=old_question,
                    new_entity=None,
                    match_type=MatchType.DELETED,
                    confidence=1.0,
                    reason="Вопрос удален",
                    external_id=old_question.external_id
                ))
        
        # Новые вопросы
        for new_question in unmatched_new:
            if new_question.external_id not in matched_new:
                matches.append(EntityMatch(
                    old_entity=None,
                    new_entity=new_question,
                    match_type=MatchType.NEW,
                    confidence=1.0,
                    reason="Новый вопрос",
                    external_id=new_question.external_id
                ))
        
        return matches
    
    def match_answers(self, old_answers: List[ChecklistAnswer], new_answers: List) -> List[EntityMatch]:
        """Сопоставляет ответы"""
        matches = []
        
        old_by_id = {a.external_id: a for a in old_answers}
        new_by_id = {a.external_id: a for a in new_answers}
        
        matched_old = set()
        matched_new = set()
        
        # Точные совпадения
        for external_id in old_by_id.keys() & new_by_id.keys():
            old_answer = old_by_id[external_id]
            new_answer = new_by_id[external_id]
            
            matches.append(EntityMatch(
                old_entity=old_answer,
                new_entity=new_answer,
                match_type=MatchType.EXACT,
                confidence=1.0,
                reason="Точное совпадение по external_id",
                external_id=external_id
            ))
            
            matched_old.add(external_id)
            matched_new.add(external_id)
        
        # Похожие ответы
        unmatched_old = [a for a in old_answers if a.external_id not in matched_old]
        unmatched_new = [a for a in new_answers if a.external_id not in matched_new]
        
        for old_answer in unmatched_old:
            best_match = None
            best_confidence = 0.0
            
            for new_answer in unmatched_new:
                if new_answer.external_id in matched_new:
                    continue
                
                confidence = self._calculate_answer_similarity(old_answer, new_answer)
                if confidence > best_confidence and confidence >= self.similarity_threshold:
                    best_match = new_answer
                    best_confidence = confidence
            
            if best_match:
                matches.append(EntityMatch(
                    old_entity=old_answer,
                    new_entity=best_match,
                    match_type=MatchType.SIMILAR,
                    confidence=best_confidence,
                    reason=f"Похожие ответы (уверенность: {best_confidence:.2f})",
                    external_id=best_match.external_id
                ))
                matched_new.add(best_match.external_id)
            else:
                matches.append(EntityMatch(
                    old_entity=old_answer,
                    new_entity=None,
                    match_type=MatchType.DELETED,
                    confidence=1.0,
                    reason="Ответ удален",
                    external_id=old_answer.external_id
                ))
        
        # Новые ответы
        for new_answer in unmatched_new:
            if new_answer.external_id not in matched_new:
                matches.append(EntityMatch(
                    old_entity=None,
                    new_entity=new_answer,
                    match_type=MatchType.NEW,
                    confidence=1.0,
                    reason="Новый ответ",
                    external_id=new_answer.external_id
                ))
        
        return matches
    
    def _calculate_section_similarity(self, old_section: ChecklistSection, new_section) -> float:
        """Вычисляет схожесть секций"""
        # Сравниваем названия
        title_similarity = self._text_similarity(old_section.title, new_section.title)
        
        # Сравниваем номера секций
        number_similarity = 1.0 if old_section.number == new_section.number else 0.0
        
        # Взвешенная оценка
        return title_similarity * 0.8 + number_similarity * 0.2
    
    def _calculate_subsection_similarity(self, old_subsection: ChecklistSubsection, new_subsection) -> float:
        """Вычисляет схожесть подсекций"""
        title_similarity = self._text_similarity(old_subsection.title, new_subsection.title)
        number_similarity = 1.0 if old_subsection.number == new_subsection.number else 0.0
        
        return title_similarity * 0.8 + number_similarity * 0.2
    
    def _calculate_group_similarity(self, old_group: ChecklistQuestionGroup, new_group) -> float:
        """Вычисляет схожесть групп вопросов"""
        return self._text_similarity(old_group.title, new_group.title)
    
    def _calculate_question_similarity(self, old_question: ChecklistQuestion, new_question) -> float:
        """Вычисляет схожесть вопросов"""
        text_similarity = self._text_similarity(old_question.text, new_question.text)
        type_similarity = 1.0 if old_question.answer_type == new_question.answer_type else 0.0
        
        return text_similarity * 0.9 + type_similarity * 0.1
    
    def _calculate_answer_similarity(self, old_answer: ChecklistAnswer, new_answer) -> float:
        """Вычисляет схожесть ответов"""
        male_similarity = self._text_similarity(old_answer.value_male, new_answer.value_male)
        female_similarity = self._text_similarity(old_answer.value_female, new_answer.value_female)
        
        return (male_similarity + female_similarity) / 2
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """
        Вычисляет схожесть текстов (простая реализация)
        
        В продакшене можно использовать более сложные алгоритмы:
        - Levenshtein distance
        - Cosine similarity
        - BERT embeddings
        """
        if not text1 or not text2:
            return 0.0
        
        if text1 == text2:
            return 1.0
        
        # Простое сравнение по словам
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union)
    
    def get_match_summary(self, matches: Dict[str, List[EntityMatch]]) -> Dict[str, Any]:
        """
        Создает сводку по результатам сопоставления
        
        Args:
            matches: Результаты сопоставления
            
        Returns:
            Сводная статистика
        """
        summary = {}
        
        for entity_type, entity_matches in matches.items():
            type_summary = {
                "total": len(entity_matches),
                "exact": 0,
                "similar": 0,
                "new": 0,
                "deleted": 0,
                "moved": 0
            }
            
            for match in entity_matches:
                type_summary[match.match_type.value] += 1
            
            summary[entity_type] = type_summary
        
        return summary


# Глобальный экземпляр сервиса
entity_matcher = EntityMatcher()