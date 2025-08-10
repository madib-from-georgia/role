"""
CRUD операции для проектов.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database.crud.base import CRUDBase
from app.database.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate


class CRUDProject(CRUDBase[Project, ProjectCreate, ProjectUpdate]):
    """CRUD операции для модели Project."""

    def create_with_owner(
        self, db: Session, *, obj_in: ProjectCreate, owner_id: int
    ) -> Project:
        """Создание проекта с указанием владельца."""
        db_obj = Project(**obj_in.model_dump(), user_id=owner_id)
        db.add(db_obj)
        try:
            db.commit()
            db.refresh(db_obj)
        except Exception as e:
            db.rollback()
            raise ValueError(f"Ошибка создания проекта: {str(e)}")
        return db_obj

    def get_multi_by_owner(
        self, db: Session, *, owner_id: int, skip: int = 0, limit: int = 100
    ) -> List[Project]:
        """Получение проектов пользователя."""
        return (
            db.query(self.model)
            .filter(Project.user_id == owner_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_title_and_owner(
        self, db: Session, *, title: str, owner_id: int
    ) -> Optional[Project]:
        """Получение проекта по названию и владельцу."""
        return (
            db.query(Project)
            .filter(Project.title == title)
            .filter(Project.user_id == owner_id)
            .first()
        )

    def count_by_owner(self, db: Session, *, owner_id: int) -> int:
        """Подсчет проектов пользователя."""
        return db.query(self.model).filter(Project.user_id == owner_id).count()

    def is_owner(self, db: Session, *, project_id: int, user_id: int) -> bool:
        """Проверка владельца проекта."""
        project = self.get(db, id=project_id)
        if not project:
            return False
        return project.user_id == user_id

    def get_with_texts(self, db: Session, *, project_id: int) -> Optional[Project]:
        """Получение проекта с текстами."""
        from app.database.models.text import Text
        return (
            db.query(Project)
            .filter(Project.id == project_id)
            .join(Text, isouter=True)
            .first()
        )
    
    def get_user_projects(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Project]:
        """Получение проектов пользователя (alias для get_multi_by_owner)."""
        return self.get_multi_by_owner(db, owner_id=user_id, skip=skip, limit=limit)

    def remove(self, db: Session, *, id: int) -> Project:
        """
        Удаление проекта с правильным каскадным удалением связанных записей.
        
        Порядок удаления:
        1. ChecklistResponseHistory (история ответов)
        2. ChecklistResponse (ответы на вопросы чеклистов)
        3. Character (персонажи)
        4. Text (тексты)
        5. Project (сам проект)
        """
        from app.database.models.text import Text
        from app.database.models.character import Character
        from app.database.models.checklist import ChecklistResponse, ChecklistResponseHistory
        
        # Получаем проект
        project = db.query(self.model).get(id)
        if not project:
            raise ValueError(f"Проект с ID {id} не найден")
        
        try:
            # Собираем все ID ответов на чеклисты для удаления истории
            response_ids = []
            for text in project.texts:
                for character in text.characters:
                    character_responses = db.query(ChecklistResponse.id).filter(
                        ChecklistResponse.character_id == character.id
                    ).all()
                    response_ids.extend([r.id for r in character_responses])
            
            # 1. Удаляем историю ответов на чеклисты
            if response_ids:
                db.query(ChecklistResponseHistory).filter(
                    ChecklistResponseHistory.response_id.in_(response_ids)
                ).delete(synchronize_session=False)
            
            # 2. Удаляем все ответы на чеклисты для всех персонажей проекта
            for text in project.texts:
                for character in text.characters:
                    db.query(ChecklistResponse).filter(
                        ChecklistResponse.character_id == character.id
                    ).delete(synchronize_session=False)
            
            # 3. Удаляем всех персонажей
            for text in project.texts:
                db.query(Character).filter(
                    Character.text_id == text.id
                ).delete(synchronize_session=False)
            
            # 4. Удаляем все тексты
            db.query(Text).filter(
                Text.project_id == project.id
            ).delete(synchronize_session=False)
            
            # 5. Удаляем сам проект
            db.delete(project)
            db.commit()
            
        except IntegrityError as e:
            db.rollback()
            raise ValueError(f"Ошибка удаления записи: {str(e)}")
        except Exception as e:
            db.rollback()
            raise ValueError(f"Неожиданная ошибка при удалении: {str(e)}")
        
        return project


project = CRUDProject(Project)
