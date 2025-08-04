"""
CRUD операции для ответов на вопросы чеклистов
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import and_, desc
from datetime import datetime

from app.database.crud.base import CRUDBase
from app.database.models.checklist import ChecklistResponse, ChecklistResponseHistory, SourceType
from app.schemas.checklist import ChecklistResponseCreate, ChecklistResponseUpdate


class CRUDChecklistResponse(CRUDBase[ChecklistResponse, ChecklistResponseCreate, ChecklistResponseUpdate]):
    """CRUD операции для ответов на вопросы чеклистов"""
    
    def get_by_character_and_question(
        self, 
        db: Session, 
        character_id: int, 
        question_id: int
    ) -> Optional[ChecklistResponse]:
        """Получение текущего ответа персонажа на вопрос"""
        return db.query(ChecklistResponse).filter(
            and_(
                ChecklistResponse.character_id == character_id,
                ChecklistResponse.question_id == question_id,
                ChecklistResponse.is_current == True
            )
        ).first()
    
    def get_by_character(self, db: Session, character_id: int) -> List[ChecklistResponse]:
        """Получение всех текущих ответов персонажа"""
        return db.query(ChecklistResponse).filter(
            and_(
                ChecklistResponse.character_id == character_id,
                ChecklistResponse.is_current == True
            )
        ).all()
    
    def get_by_character_and_checklist(
        self, 
        db: Session, 
        character_id: int, 
        checklist_id: int
    ) -> List[ChecklistResponse]:
        """Получение ответов персонажа по конкретному чеклисту"""
        from app.database.models.checklist import ChecklistQuestion, ChecklistQuestionGroup, ChecklistSubsection, ChecklistSection
        
        return db.query(ChecklistResponse).join(
            ChecklistQuestion, ChecklistResponse.question_id == ChecklistQuestion.id
        ).join(
            ChecklistQuestionGroup, ChecklistQuestion.question_group_id == ChecklistQuestionGroup.id
        ).join(
            ChecklistSubsection, ChecklistQuestionGroup.subsection_id == ChecklistSubsection.id
        ).join(
            ChecklistSection, ChecklistSubsection.section_id == ChecklistSection.id
        ).filter(
            and_(
                ChecklistResponse.character_id == character_id,
                ChecklistResponse.is_current == True,
                ChecklistSection.checklist_id == checklist_id
            )
        ).all()
    
    def create_or_update_response(
        self, 
        db: Session, 
        character_id: int, 
        question_id: int, 
        response_data: ChecklistResponseUpdate,
        change_reason: Optional[str] = None
    ) -> ChecklistResponse:
        """
        Создание нового ответа или обновление существующего с версионированием
        """
        # Ищем существующий ответ
        existing_response = self.get_by_character_and_question(db, character_id, question_id)
        
        if existing_response:
            # Обновляем существующий ответ
            return self._update_with_versioning(db, existing_response, response_data, change_reason)
        else:
            # Создаем новый ответ
            create_data = ChecklistResponseCreate(
                question_id=question_id,
                character_id=character_id,
                answer=response_data.answer,
                source_type=response_data.source_type,
                comment=response_data.comment
            )
            return self.create(db, obj_in=create_data)
    
    def _update_with_versioning(
        self, 
        db: Session, 
        response: ChecklistResponse, 
        update_data: ChecklistResponseUpdate,
        change_reason: Optional[str] = None
    ) -> ChecklistResponse:
        """Обновление ответа с сохранением предыдущей версии"""
        # Сохраняем предыдущую версию в историю
        history_entry = ChecklistResponseHistory(
            response_id=response.id,
            previous_answer=response.answer,
            previous_source_type=response.source_type,
            previous_comment=response.comment,
            previous_version=response.version,
            change_reason=change_reason or "Обновление ответа"
        )
        db.add(history_entry)
        
        # Обновляем текущий ответ
        response.answer = update_data.answer
        response.source_type = update_data.source_type
        response.comment = update_data.comment
        response.version += 1
        response.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(response)
        return response
    
    def delete_response(
        self, 
        db: Session, 
        response_id: int, 
        delete_reason: str = "Удаление ответа"
    ) -> bool:
        """
        Удаление ответа с сохранением в истории
        """
        response = self.get(db, id=response_id)
        if not response:
            return False
        
        # Сохраняем в историю перед удалением
        history_entry = ChecklistResponseHistory(
            response_id=response.id,
            previous_answer=response.answer,
            previous_source_type=response.source_type,
            previous_comment=response.comment,
            previous_version=response.version,
            change_reason=delete_reason
        )
        db.add(history_entry)
        
        # Удаляем ответ
        db.delete(response)
        db.commit()
        return True
    
    def get_response_history(self, db: Session, response_id: int) -> List[ChecklistResponseHistory]:
        """Получение истории изменений ответа"""
        return db.query(ChecklistResponseHistory).filter(
            ChecklistResponseHistory.response_id == response_id
        ).order_by(desc(ChecklistResponseHistory.created_at)).all()
    
    def restore_from_history(
        self, 
        db: Session, 
        response_id: int, 
        history_id: int,
        restore_reason: str = "Восстановление из истории"
    ) -> Optional[ChecklistResponse]:
        """Восстановление ответа из истории"""
        response = self.get(db, id=response_id)
        history_entry = db.query(ChecklistResponseHistory).filter(
            ChecklistResponseHistory.id == history_id
        ).first()
        
        if not response or not history_entry:
            return None
        
        # Сохраняем текущее состояние в историю
        current_history = ChecklistResponseHistory(
            response_id=response.id,
            previous_answer=response.answer,
            previous_source_type=response.source_type,
            previous_comment=response.comment,
            previous_version=response.version,
            change_reason=f"Перед восстановлением: {restore_reason}"
        )
        db.add(current_history)
        
        # Восстанавливаем из истории
        response.answer = history_entry.previous_answer
        response.source_type = history_entry.previous_source_type
        response.comment = history_entry.previous_comment
        response.version += 1
        response.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(response)
        return response
    
    def get_completion_stats(self, db: Session, character_id: int, checklist_id: int) -> Dict[str, Any]:
        """Получение статистики заполнения чеклиста для персонажа"""
        from app.database.crud.crud_checklist import checklist_question
        
        # Общее количество вопросов в чеклисте
        total_questions = checklist_question.get_by_checklist(db, checklist_id)
        total_count = len(total_questions)
        
        # Количество отвеченных вопросов
        answered_responses = self.get_by_character_and_checklist(db, character_id, checklist_id)
        answered_count = len([r for r in answered_responses if r.answer])
        
        # Распределение по источникам ответов
        source_distribution = {}
        for response in answered_responses:
            if response.source_type:
                source_type = response.source_type.value
                source_distribution[source_type] = source_distribution.get(source_type, 0) + 1
        
        # Процент заполнения
        completion_percentage = (answered_count / total_count * 100) if total_count > 0 else 0
        
        # Последнее обновление
        last_updated = None
        if answered_responses:
            last_updated = max(r.updated_at or r.created_at for r in answered_responses)
        
        return {
            "total_questions": total_count,
            "answered_questions": answered_count,
            "completion_percentage": round(completion_percentage, 1),
            "answers_by_source": source_distribution,
            "last_updated": last_updated
        }
    
    def bulk_update_responses(
        self, 
        db: Session, 
        character_id: int, 
        updates: List[Dict[str, Any]]
    ) -> List[ChecklistResponse]:
        """Массовое обновление ответов"""
        updated_responses = []
        
        for update_data in updates:
            question_id = update_data.get("question_id")
            if not question_id:
                continue
            
            response_update = ChecklistResponseUpdate(
                answer=update_data.get("answer"),
                source_type=update_data.get("source_type"),
                comment=update_data.get("comment"),
                change_reason=update_data.get("change_reason", "Массовое обновление")
            )
            
            response = self.create_or_update_response(
                db, character_id, question_id, response_update, "Массовое обновление"
            )
            updated_responses.append(response)
        
        return updated_responses


class CRUDChecklistResponseHistory(CRUDBase[ChecklistResponseHistory, dict, dict]):
    """CRUD операции для истории ответов"""
    
    def get_by_response(self, db: Session, response_id: int) -> List[ChecklistResponseHistory]:
        """Получение истории конкретного ответа"""
        return db.query(ChecklistResponseHistory).filter(
            ChecklistResponseHistory.response_id == response_id
        ).order_by(desc(ChecklistResponseHistory.created_at)).all()
    
    def get_by_character(self, db: Session, character_id: int, limit: int = 50) -> List[ChecklistResponseHistory]:
        """Получение последних изменений по персонажу"""
        return db.query(ChecklistResponseHistory).join(
            ChecklistResponse, ChecklistResponseHistory.response_id == ChecklistResponse.id
        ).filter(
            ChecklistResponse.character_id == character_id
        ).order_by(desc(ChecklistResponseHistory.created_at)).limit(limit).all()


# Инициализация CRUD объектов
checklist_response = CRUDChecklistResponse(ChecklistResponse)
checklist_response_history = CRUDChecklistResponseHistory(ChecklistResponseHistory)