"""
Сервис для работы с чеклистами
"""

from typing import List, Optional, Dict, Any
from pathlib import Path
from sqlalchemy.orm import Session
from loguru import logger

from app.services.checklist_json_parser_new import ChecklistJsonParserNew
from app.database.crud.crud_checklist import (
    checklist as checklist_crud,
    checklist_section,
    checklist_subsection,
    checklist_question_group,
    checklist_question,
    checklist_answer
)
from app.database.crud.crud_checklist_response import checklist_response
from app.database.models.checklist import (
    Checklist, ChecklistSection, ChecklistSubsection,
    ChecklistQuestionGroup, ChecklistQuestion, ChecklistAnswer
)
from app.schemas.checklist import (
    ChecklistCreate, ChecklistWithResponses, ChecklistStats,
    ChecklistResponseCreate, ChecklistResponseUpdate
)


class ChecklistService:
    """
    Сервис для управления чеклистами
    
    Объединяет парсинг чеклистов из Markdown файлов,
    сохранение в базу данных и работу с ответами пользователей
    """
    
    def __init__(self):
        self.parser = ChecklistJsonParserNew()
    
    def import_checklist_from_file(self, db: Session, file_path: str) -> Checklist:
        """
        Импорт чеклиста из JSON файла в базу данных
        
        Args:
            db: Сессия базы данных
            file_path: Путь к JSON файлу чеклиста
            
        Returns:
            Созданный чеклист
        """
        logger.info(f"Импорт чеклиста из файла: {file_path}")
        
        # Парсим файл
        structure = self.parser.parse_file(file_path)
        
        # Проверяем, не существует ли уже чеклист с таким external_id
        existing = checklist_crud.get_by_external_id(db, structure.external_id)
        if existing:
            logger.warning(f"Чеклист с external_id '{structure.external_id}' уже существует")
            raise ValueError(f"Чеклист с external_id '{structure.external_id}' уже существует")
        
        # Создаем чеклист
        checklist_data = ChecklistCreate(
            external_id=structure.external_id,
            title=structure.title,
            description=structure.description or f"Импортирован из файла {Path(file_path).name}",
            slug=structure.slug,
            icon=structure.icon,
            order_index=0,
            is_active=True,
            goal=structure.goal,
            file_hash=structure.file_hash,
            version=structure.version
        )
        
        checklist_obj = checklist_crud.create(db, obj_in=checklist_data)
        
        # Создаем структуру
        self._create_checklist_structure(db, checklist_obj.id, structure)
        
        logger.success(f"Чеклист '{structure.title}' успешно импортирован")
        return checklist_obj
    
    def _create_checklist_structure(self, db: Session, checklist_id: int, structure):
        """Создает структуру чеклиста в базе данных"""
        
        for section_data in structure.sections:
            # Создаем секцию
            section_obj = ChecklistSection(
                checklist_id=checklist_id,
                external_id=section_data.external_id,
                title=section_data.title,
                number=section_data.number,
                icon=section_data.icon,
                order_index=section_data.order_index
            )
            db.add(section_obj)
            db.flush()  # Получаем ID
            
            for subsection_data in section_data.subsections:
                # Создаем подсекцию
                subsection_obj = ChecklistSubsection(
                    section_id=section_obj.id,
                    external_id=subsection_data.external_id,
                    title=subsection_data.title,
                    number=subsection_data.number,
                    order_index=subsection_data.order_index
                )
                db.add(subsection_obj)
                db.flush()
                
                for group_data in subsection_data.question_groups:
                    # Создаем группу вопросов
                    group_obj = ChecklistQuestionGroup(
                        subsection_id=subsection_obj.id,
                        external_id=group_data.external_id,
                        title=group_data.title,
                        order_index=group_data.order_index
                    )
                    db.add(group_obj)
                    db.flush()
                    
                    for question_data in group_data.questions:
                        # Создаем вопрос
                        question_obj = ChecklistQuestion(
                            question_group_id=group_obj.id,
                            external_id=question_data.external_id,
                            text=question_data.text,
                            order_index=question_data.order_index,
                            answer_type=question_data.answer_type,
                            source_type=question_data.source_type
                        )
                        db.add(question_obj)
                        db.flush()
                        
                        # Создаем ответы для вопроса
                        for answer_data in question_data.answers:
                            answer_obj = ChecklistAnswer(
                                question_id=question_obj.id,
                                external_id=answer_data.external_id,
                                value_male=answer_data.value_male,
                                value_female=answer_data.value_female,
                                exported_value_male=answer_data.exported_value_male,
                                exported_value_female=answer_data.exported_value_female,
                                hint=answer_data.hint,
                                order_index=answer_data.order_index
                            )
                            db.add(answer_obj)
        
        db.commit()
    
    def get_checklist_with_responses(
        self, 
        db: Session, 
        checklist_slug: str, 
        character_id: int
    ) -> Optional[ChecklistWithResponses]:
        """
        Получение чеклиста с ответами конкретного персонажа
        
        Args:
            db: Сессия базы данных
            checklist_slug: Slug чеклиста
            character_id: ID персонажа
            
        Returns:
            Чеклист с ответами или None
        """
        # Получаем чеклист с полной структурой
        checklist_obj = checklist_crud.get_by_slug_with_structure(db, checklist_slug)
        if not checklist_obj:
            return None
        
        # Получаем все ответы персонажа для этого чеклиста
        responses = checklist_response.get_by_character_and_checklist(
            db, character_id, checklist_obj.id
        )
        
        # Создаем словарь ответов по question_id для быстрого поиска
        responses_dict = {r.question_id: r for r in responses}
        
        # Обогащаем структуру ответами
        enriched_checklist = self._enrich_checklist_with_responses(
            checklist_obj, responses_dict
        )
        
        # Добавляем статистику заполнения
        stats = checklist_response.get_completion_stats(db, character_id, checklist_obj.id)
        enriched_checklist.completion_stats = stats
        
        return enriched_checklist
    
    def _enrich_checklist_with_responses(
        self, 
        checklist_obj: Checklist, 
        responses_dict: Dict[int, Any]
    ) -> ChecklistWithResponses:
        """Обогащает структуру чеклиста ответами"""
        from app.schemas.checklist import (
            ChecklistWithResponses, ChecklistSectionWithResponses,
            ChecklistSubsectionWithResponses, ChecklistQuestionGroupWithResponses,
            ChecklistQuestionWithResponse
        )
        
        # Создаем обогащенные секции
        enriched_sections = []
        for section in checklist_obj.sections:
            enriched_subsections = []
            
            for subsection in section.subsections:
                enriched_question_groups = []
                
                for question_group in subsection.question_groups:
                    enriched_questions = []
                    
                    for question in question_group.questions:
                        # Получаем ответ для этого вопроса
                        current_response = responses_dict.get(question.id)
                        
                        # Создаем обогащенный вопрос
                        enriched_question = ChecklistQuestionWithResponse(
                            id=question.id,
                            external_id=question.external_id,
                            text=question.text,
                            order_index=question.order_index,
                            answer_type=question.answer_type,
                            source_type=question.source_type,
                            question_group_id=question.question_group_id,
                            answers=question.answers,
                            created_at=question.created_at,
                            current_response=current_response,
                            response_history=[]  # TODO: Добавить историю ответов
                        )
                        enriched_questions.append(enriched_question)
                    
                    # Создаем обогащенную группу вопросов
                    enriched_group = ChecklistQuestionGroupWithResponses(
                        id=question_group.id,
                        external_id=question_group.external_id,
                        title=question_group.title,
                        order_index=question_group.order_index,
                        subsection_id=question_group.subsection_id,
                        questions=enriched_questions
                    )
                    enriched_question_groups.append(enriched_group)
                
                # Создаем обогащенную подсекцию
                enriched_subsection = ChecklistSubsectionWithResponses(
                    id=subsection.id,
                    external_id=subsection.external_id,
                    title=subsection.title,
                    number=subsection.number,
                    order_index=subsection.order_index,
                    section_id=subsection.section_id,
                    question_groups=enriched_question_groups
                )
                enriched_subsections.append(enriched_subsection)
            
            # Создаем обогащенную секцию
            enriched_section = ChecklistSectionWithResponses(
                id=section.id,
                external_id=section.external_id,
                title=section.title,
                number=section.number,
                icon=section.icon,
                order_index=section.order_index,
                checklist_id=section.checklist_id,
                subsections=enriched_subsections
            )
            enriched_sections.append(enriched_section)
        
        # Создаем обогащенный чеклист
        enriched_checklist = ChecklistWithResponses(
            id=checklist_obj.id,
            external_id=checklist_obj.external_id,
            title=checklist_obj.title,
            description=checklist_obj.description,
            slug=checklist_obj.slug,
            icon=checklist_obj.icon,
            order_index=checklist_obj.order_index,
            is_active=checklist_obj.is_active,
            goal=checklist_obj.goal,
            file_hash=checklist_obj.file_hash,
            version=checklist_obj.version,
            created_at=checklist_obj.created_at,
            updated_at=checklist_obj.updated_at,
            sections=enriched_sections
        )
        
        return enriched_checklist
    
    def update_response(
        self, 
        db: Session, 
        character_id: int, 
        question_id: int, 
        response_data: ChecklistResponseUpdate
    ) -> Optional[Any]:
        """
        Обновление ответа на вопрос
        
        Args:
            db: Сессия базы данных
            character_id: ID персонажа
            question_id: ID вопроса
            response_data: Данные ответа
            
        Returns:
            Обновленный ответ
        """
        return checklist_response.create_or_update_response(
            db, character_id, question_id, response_data,
            change_reason=response_data.change_reason
        )
    
    def delete_response(
        self, 
        db: Session, 
        response_id: int, 
        delete_reason: str = "Удаление пользователем"
    ) -> bool:
        """
        Удаление ответа с сохранением в истории
        
        Args:
            db: Сессия базы данных
            response_id: ID ответа
            delete_reason: Причина удаления
            
        Returns:
            True если удаление успешно
        """
        return checklist_response.delete_response(db, response_id, delete_reason)
    
    def restore_response_version(
        self, 
        db: Session, 
        response_id: int, 
        history_id: int,
        restore_reason: str = "Восстановление пользователем"
    ) -> Optional[Any]:
        """
        Восстановление предыдущей версии ответа
        
        Args:
            db: Сессия базы данных
            response_id: ID ответа
            history_id: ID версии для восстановления
            restore_reason: Причина восстановления
            
        Returns:
            Восстановленный ответ
        """
        return checklist_response.restore_from_history(
            db, response_id, history_id, restore_reason
        )
    
    def get_character_progress(self, db: Session, character_id: int) -> List[ChecklistStats]:
        """
        Получение прогресса заполнения всех чеклистов для персонажа
        
        Args:
            db: Сессия базы данных
            character_id: ID персонажа
            
        Returns:
            Список статистик по чеклистам
        """
        checklists = checklist_crud.get_active_checklists(db)
        progress = []
        
        for checklist_obj in checklists:
            stats = checklist_response.get_completion_stats(db, character_id, checklist_obj.id)
            
            checklist_stats = ChecklistStats(
                checklist_id=checklist_obj.id,
                total_questions=stats["total_questions"],
                answered_questions=stats["answered_questions"],
                completion_percentage=stats["completion_percentage"],
                answers_by_source=stats["answers_by_source"],
                last_updated=stats["last_updated"]
            )
            progress.append(checklist_stats)
        
        return progress
    
    def search_questions(
        self, 
        db: Session, 
        query: str, 
        checklist_slug: Optional[str] = None
    ) -> List[ChecklistQuestion]:
        """
        Поиск вопросов по тексту
        
        Args:
            db: Сессия базы данных
            query: Поисковый запрос
            checklist_slug: Ограничить поиск конкретным чеклистом
            
        Returns:
            Список найденных вопросов
        """
        checklist_id = None
        if checklist_slug:
            checklist_obj = checklist_crud.get_by_slug(db, checklist_slug)
            if checklist_obj:
                checklist_id = checklist_obj.id
        
        return checklist_question.search_questions(db, query, checklist_id)
    
    def get_available_checklists(self, db: Session, character_id: Optional[int] = None) -> List[Checklist]:
        """
        Получение списка доступных чеклистов
        
        Args:
            db: Сессия базы данных
            character_id: ID персонажа для получения статистики (опционально)
            
        Returns:
            Список чеклистов с опциональной статистикой заполнения
        """
        checklists = checklist_crud.get_multi(db)
        
        # Если указан character_id, добавляем статистику для каждого чеклиста
        if character_id:
            enriched_checklists = []
            for checklist_obj in checklists:
                # Получаем статистику заполнения
                stats = checklist_response.get_completion_stats(db, character_id, checklist_obj.id)
                
                # Создаем обогащенный чеклист
                from app.schemas.checklist import Checklist
                enriched_checklist = Checklist(
                    id=checklist_obj.id,
                    external_id=checklist_obj.external_id,
                    title=checklist_obj.title,
                    description=checklist_obj.description,
                    slug=checklist_obj.slug,
                    icon=checklist_obj.icon,
                    order_index=checklist_obj.order_index,
                    is_active=checklist_obj.is_active,
                    goal=checklist_obj.goal,
                    file_hash=checklist_obj.file_hash,
                    version=checklist_obj.version,
                    created_at=checklist_obj.created_at,
                    updated_at=checklist_obj.updated_at,
                    sections=[],  # Для списка чеклистов секции не нужны
                    completion_stats=stats
                )
                enriched_checklists.append(enriched_checklist)
            
            return enriched_checklists
        
        return checklists
    
    def get_checklist_structure(self, db: Session, checklist_slug: str) -> Optional[ChecklistWithResponses]:
        """
        Получение структуры чеклиста без привязки к персонажу
        
        Args:
            db: Сессия базы данных
            checklist_slug: Slug чеклиста
            
        Returns:
            Структура чеклиста с пустыми ответами
        """
        checklist_obj = checklist_crud.get_by_slug_with_structure(db, checklist_slug)
        
        if not checklist_obj:
            return None
        
        # Создаем структуру с пустыми ответами
        return self._enrich_checklist_with_responses(checklist_obj, {})
    
    def validate_checklist_file(self, file_path: str) -> Dict[str, Any]:
        """
        Валидация файла чеклиста без импорта в БД
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            Результат валидации с краткой информацией
        """
        try:
            structure = self.parser.parse_file(file_path)
            summary = self.parser.get_structure_summary(structure)
            
            return {
                "valid": True,
                "summary": summary,
                "errors": []
            }
        except Exception as e:
            return {
                "valid": False,
                "summary": None,
                "errors": [str(e)]
            }


# Глобальный экземпляр сервиса
checklist_service = ChecklistService()
