"""
CRUD операции для проектов.
"""

from typing import List, Optional
from sqlalchemy.orm import Session

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


project = CRUDProject(Project)
