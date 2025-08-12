"""
CRUD операции для чеклистов
"""

from typing import List, Optional
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import and_

from app.database.crud.base import CRUDBase
from app.database.models.checklist import (
    Checklist, ChecklistSection, ChecklistSubsection,
    ChecklistQuestionGroup, ChecklistQuestion, ChecklistAnswer
)
from app.schemas.checklist import ChecklistCreate, ChecklistUpdate


class CRUDChecklist(CRUDBase[Checklist, ChecklistCreate, ChecklistUpdate]):
    """CRUD операции для чеклистов"""
    
    def get_with_full_structure(self, db: Session, id: int) -> Optional[Checklist]:
        """
        Получение чеклиста с полной структурой (секции, подсекции, группы, вопросы, ответы)
        """
        return db.query(Checklist).options(
            selectinload(Checklist.sections).selectinload(ChecklistSection.subsections)
            .selectinload(ChecklistSubsection.question_groups)
            .selectinload(ChecklistQuestionGroup.questions)
            .selectinload(ChecklistQuestion.answers)
        ).filter(Checklist.id == id).first()
    
    def get_by_slug(self, db: Session, slug: str) -> Optional[Checklist]:
        """Получение чеклиста по slug"""
        return db.query(Checklist).filter(Checklist.slug == slug).first()
    
    def get_by_external_id(self, db: Session, external_id: str) -> Optional[Checklist]:
        """Получение чеклиста по external_id"""
        return db.query(Checklist).filter(Checklist.external_id == external_id).first()
    
    def get_by_slug_with_structure(self, db: Session, slug: str) -> Optional[Checklist]:
        """Получение чеклиста по slug с полной структурой"""
        return db.query(Checklist).options(
            selectinload(Checklist.sections).selectinload(ChecklistSection.subsections)
            .selectinload(ChecklistSubsection.question_groups)
            .selectinload(ChecklistQuestionGroup.questions)
            .selectinload(ChecklistQuestion.answers)
        ).filter(Checklist.slug == slug).first()
    
    def get_by_file_hash(self, db: Session, file_hash: str) -> Optional[Checklist]:
        """Получение чеклиста по хешу файла"""
        return db.query(Checklist).filter(Checklist.file_hash == file_hash).first()
    
    def delete_by_slug(self, db: Session, slug: str) -> bool:
        """Удаление чеклиста по slug"""
        checklist_obj = self.get_by_slug(db, slug)
        if checklist_obj:
            db.delete(checklist_obj)
            db.commit()
            return True
        return False
    
    def get_active_checklists(self, db: Session) -> List[Checklist]:
        """Получение всех активных чеклистов"""
        return db.query(Checklist).filter(
            Checklist.is_active == True
        ).order_by(Checklist.order_index).all()
    
    def get_checklists_summary(self, db: Session) -> List[Checklist]:
        """Получение списка чеклистов без детальной структуры"""
        return db.query(Checklist).order_by(Checklist.order_index).all()


class CRUDChecklistSection(CRUDBase[ChecklistSection, dict, dict]):
    """CRUD операции для секций чеклистов"""
    
    def get_by_checklist(self, db: Session, checklist_id: int) -> List[ChecklistSection]:
        """Получение всех секций чеклиста"""
        return db.query(ChecklistSection).filter(
            ChecklistSection.checklist_id == checklist_id
        ).order_by(ChecklistSection.order_index).all()
    
    def get_by_external_id(self, db: Session, external_id: str, checklist_id: int) -> Optional[ChecklistSection]:
        """Получение секции по external_id в рамках чеклиста"""
        return db.query(ChecklistSection).filter(
            and_(ChecklistSection.external_id == external_id, ChecklistSection.checklist_id == checklist_id)
        ).first()
    
    def get_with_subsections(self, db: Session, section_id: int) -> Optional[ChecklistSection]:
        """Получение секции с подсекциями"""
        return db.query(ChecklistSection).options(
            selectinload(ChecklistSection.subsections)
            .selectinload(ChecklistSubsection.question_groups)
            .selectinload(ChecklistQuestionGroup.questions)
            .selectinload(ChecklistQuestion.answers)
        ).filter(ChecklistSection.id == section_id).first()


class CRUDChecklistSubsection(CRUDBase[ChecklistSubsection, dict, dict]):
    """CRUD операции для подсекций чеклистов"""
    
    def get_by_section(self, db: Session, section_id: int) -> List[ChecklistSubsection]:
        """Получение всех подсекций секции"""
        return db.query(ChecklistSubsection).filter(
            ChecklistSubsection.section_id == section_id
        ).order_by(ChecklistSubsection.order_index).all()
    
    def get_by_external_id(self, db: Session, external_id: str, section_id: int) -> Optional[ChecklistSubsection]:
        """Получение подсекции по external_id в рамках секции"""
        return db.query(ChecklistSubsection).filter(
            and_(ChecklistSubsection.external_id == external_id, ChecklistSubsection.section_id == section_id)
        ).first()
    
    def get_with_questions(self, db: Session, subsection_id: int) -> Optional[ChecklistSubsection]:
        """Получение подсекции с группами вопросов"""
        return db.query(ChecklistSubsection).options(
            selectinload(ChecklistSubsection.question_groups)
            .selectinload(ChecklistQuestionGroup.questions)
            .selectinload(ChecklistQuestion.answers)
        ).filter(ChecklistSubsection.id == subsection_id).first()


class CRUDChecklistQuestionGroup(CRUDBase[ChecklistQuestionGroup, dict, dict]):
    """CRUD операции для групп вопросов"""
    
    def get_by_subsection(self, db: Session, subsection_id: int) -> List[ChecklistQuestionGroup]:
        """Получение всех групп вопросов подсекции"""
        return db.query(ChecklistQuestionGroup).filter(
            ChecklistQuestionGroup.subsection_id == subsection_id
        ).order_by(ChecklistQuestionGroup.order_index).all()
    
    def get_by_external_id(self, db: Session, external_id: str, subsection_id: int) -> Optional[ChecklistQuestionGroup]:
        """Получение группы вопросов по external_id в рамках подсекции"""
        return db.query(ChecklistQuestionGroup).filter(
            and_(ChecklistQuestionGroup.external_id == external_id, ChecklistQuestionGroup.subsection_id == subsection_id)
        ).first()
    
    def get_with_questions(self, db: Session, group_id: int) -> Optional[ChecklistQuestionGroup]:
        """Получение группы с вопросами"""
        return db.query(ChecklistQuestionGroup).options(
            selectinload(ChecklistQuestionGroup.questions)
            .selectinload(ChecklistQuestion.answers)
        ).filter(ChecklistQuestionGroup.id == group_id).first()


class CRUDChecklistQuestion(CRUDBase[ChecklistQuestion, dict, dict]):
    """CRUD операции для вопросов чеклистов"""
    
    def get_by_group(self, db: Session, group_id: int) -> List[ChecklistQuestion]:
        """Получение всех вопросов группы"""
        return db.query(ChecklistQuestion).options(
            selectinload(ChecklistQuestion.answers)
        ).filter(
            ChecklistQuestion.question_group_id == group_id
        ).order_by(ChecklistQuestion.order_index).all()
    
    def get_by_external_id(self, db: Session, external_id: str, group_id: int) -> Optional[ChecklistQuestion]:
        """Получение вопроса по external_id в рамках группы"""
        return db.query(ChecklistQuestion).options(
            selectinload(ChecklistQuestion.answers)
        ).filter(
            and_(ChecklistQuestion.external_id == external_id, ChecklistQuestion.question_group_id == group_id)
        ).first()
    
    def get_by_checklist(self, db: Session, checklist_id: int) -> List[ChecklistQuestion]:
        """Получение всех вопросов чеклиста"""
        return db.query(ChecklistQuestion).options(
            selectinload(ChecklistQuestion.answers)
        ).join(
            ChecklistQuestionGroup, ChecklistQuestion.question_group_id == ChecklistQuestionGroup.id
        ).join(
            ChecklistSubsection, ChecklistQuestionGroup.subsection_id == ChecklistSubsection.id
        ).join(
            ChecklistSection, ChecklistSubsection.section_id == ChecklistSection.id
        ).filter(
            ChecklistSection.checklist_id == checklist_id
        ).order_by(
            ChecklistSection.order_index,
            ChecklistSubsection.order_index,
            ChecklistQuestionGroup.order_index,
            ChecklistQuestion.order_index
        ).all()
    
    def search_questions(self, db: Session, query: str, checklist_id: Optional[int] = None) -> List[ChecklistQuestion]:
        """Поиск вопросов по тексту"""
        filters = [ChecklistQuestion.text.ilike(f'%{query}%')]
        
        if checklist_id:
            query_obj = db.query(ChecklistQuestion).options(
                selectinload(ChecklistQuestion.answers)
            ).join(
                ChecklistQuestionGroup, ChecklistQuestion.question_group_id == ChecklistQuestionGroup.id
            ).join(
                ChecklistSubsection, ChecklistQuestionGroup.subsection_id == ChecklistSubsection.id
            ).join(
                ChecklistSection, ChecklistSubsection.section_id == ChecklistSection.id
            ).filter(
                and_(ChecklistSection.checklist_id == checklist_id, *filters)
            )
        else:
            query_obj = db.query(ChecklistQuestion).options(
                selectinload(ChecklistQuestion.answers)
            ).filter(and_(*filters))
        
        return query_obj.limit(50).all()


class CRUDChecklistAnswer(CRUDBase[ChecklistAnswer, dict, dict]):
    """CRUD операции для ответов на вопросы"""
    
    def get_by_question(self, db: Session, question_id: int) -> List[ChecklistAnswer]:
        """Получение всех ответов для вопроса"""
        return db.query(ChecklistAnswer).filter(
            ChecklistAnswer.question_id == question_id
        ).order_by(ChecklistAnswer.order_index).all()
    
    def get_by_external_id(self, db: Session, external_id: str, question_id: int) -> Optional[ChecklistAnswer]:
        """Получение ответа по external_id в рамках вопроса"""
        return db.query(ChecklistAnswer).filter(
            and_(ChecklistAnswer.external_id == external_id, ChecklistAnswer.question_id == question_id)
        ).first()


# Инициализация CRUD объектов
checklist = CRUDChecklist(Checklist)
checklist_section = CRUDChecklistSection(ChecklistSection)
checklist_subsection = CRUDChecklistSubsection(ChecklistSubsection)
checklist_question_group = CRUDChecklistQuestionGroup(ChecklistQuestionGroup)
checklist_question = CRUDChecklistQuestion(ChecklistQuestion)
checklist_answer = CRUDChecklistAnswer(ChecklistAnswer)
