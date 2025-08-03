"""
CRUD операции для чеклистов.
"""

from typing import List, Optional, Dict
from sqlalchemy.orm import Session

from app.database.crud.base import CRUDBase
from app.database.models.checklist import ChecklistResponse
from app.schemas.checklist import ChecklistResponseCreate, ChecklistResponseUpdate


class CRUDChecklistResponse(CRUDBase[ChecklistResponse, ChecklistResponseCreate, ChecklistResponseUpdate]):
    """CRUD операции для модели ChecklistResponse."""

    def get_multi_by_character(
        self, db: Session, *, character_id: int, skip: int = 0, limit: int = 100
    ) -> List[ChecklistResponse]:
        """Получение ответов персонажа."""
        return (
            db.query(self.model)
            .filter(ChecklistResponse.character_id == character_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_character_and_type(
        self, db: Session, *, character_id: int, checklist_type: str
    ) -> List[ChecklistResponse]:
        """Получение ответов персонажа по типу чеклиста."""
        return (
            db.query(self.model)
            .filter(ChecklistResponse.character_id == character_id)
            .filter(ChecklistResponse.checklist_type == checklist_type)
            .all()
        )

    def get_by_character_type_and_question(
        self, 
        db: Session, 
        *, 
        character_id: int, 
        checklist_type: str, 
        question_id: str
    ) -> Optional[ChecklistResponse]:
        """Получение конкретного ответа персонажа."""
        return (
            db.query(self.model)
            .filter(ChecklistResponse.character_id == character_id)
            .filter(ChecklistResponse.checklist_type == checklist_type)
            .filter(ChecklistResponse.question_id == question_id)
            .first()
        )

    def create_or_update_response(
        self,
        db: Session,
        *,
        character_id: int,
        checklist_type: str,
        question_id: str,
        response: str,
        confidence_level: int = 3
    ) -> ChecklistResponse:
        """Создание или обновление ответа."""
        existing = self.get_by_character_type_and_question(
            db, 
            character_id=character_id,
            checklist_type=checklist_type,
            question_id=question_id
        )
        
        if existing:
            # Обновляем существующий ответ
            existing.response = response
            existing.confidence_level = confidence_level
            db.add(existing)
            db.commit()
            db.refresh(existing)
            return existing
        else:
            # Создаем новый ответ
            obj_in = ChecklistResponseCreate(
                character_id=character_id,
                checklist_type=checklist_type,
                question_id=question_id,
                response=response,
                confidence_level=confidence_level
            )
            return self.create(db, obj_in=obj_in)

    def get_completion_stats(
        self, db: Session, *, character_id: int, checklist_type: str
    ) -> Dict[str, int]:
        """Статистика заполнения чеклиста."""
        responses = self.get_by_character_and_type(
            db, character_id=character_id, checklist_type=checklist_type
        )
        
        total_responses = len(responses)
        filled_responses = len([r for r in responses if r.response and r.response.strip()])
        
        return {
            "total": total_responses,
            "filled": filled_responses,
            "empty": total_responses - filled_responses,
            "completion_percent": round((filled_responses / total_responses * 100) if total_responses > 0 else 0, 2)
        }

    def get_responses_by_confidence(
        self, 
        db: Session, 
        *, 
        character_id: int, 
        min_confidence: int = 1, 
        max_confidence: int = 5
    ) -> List[ChecklistResponse]:
        """Получение ответов по уровню уверенности."""
        return (
            db.query(self.model)
            .filter(ChecklistResponse.character_id == character_id)
            .filter(ChecklistResponse.confidence_level >= min_confidence)
            .filter(ChecklistResponse.confidence_level <= max_confidence)
            .order_by(ChecklistResponse.confidence_level.desc())
            .all()
        )

    def count_by_character(self, db: Session, *, character_id: int) -> int:
        """Подсчет ответов персонажа."""
        return db.query(self.model).filter(ChecklistResponse.character_id == character_id).count()

    def count_by_type(self, db: Session, *, checklist_type: str) -> int:
        """Подсчет ответов по типу чеклиста."""
        return db.query(self.model).filter(ChecklistResponse.checklist_type == checklist_type).count()

    def get_all_types(self, db: Session) -> List[str]:
        """Получение всех типов чеклистов."""
        result = db.query(ChecklistResponse.checklist_type).distinct().all()
        return [row[0] for row in result]

    def belongs_to_character(
        self, db: Session, *, response_id: int, character_id: int
    ) -> bool:
        """Проверка принадлежности ответа к персонажу."""
        response = self.get(db, id=response_id)
        if not response:
            return False
        return response.character_id == character_id


checklist_response = CRUDChecklistResponse(ChecklistResponse)
