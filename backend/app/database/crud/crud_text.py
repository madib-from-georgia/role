"""
CRUD операции для текстов произведений.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from app.database.crud.base import CRUDBase
from app.database.models.text import Text
from app.schemas.text import TextCreate, TextUpdate


class CRUDText(CRUDBase[Text, TextCreate, TextUpdate]):
    """CRUD операции для модели Text."""

    def get_multi_by_project(
        self, db: Session, *, project_id: int, skip: int = 0, limit: int = 100
    ) -> List[Text]:
        """Получение текстов проекта."""
        return (
            db.query(self.model)
            .filter(Text.project_id == project_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_filename_and_project(
        self, db: Session, *, filename: str, project_id: int
    ) -> Optional[Text]:
        """Получение текста по имени файла и проекту."""
        return (
            db.query(Text)
            .filter(Text.filename == filename)
            .filter(Text.project_id == project_id)
            .first()
        )

    def mark_as_processed(self, db: Session, *, text_id: int) -> Optional[Text]:
        """Отметка текста как обработанного."""
        text = self.get(db, id=text_id)
        if not text:
            return None
        
        text.processed_at = datetime.utcnow()
        db.add(text)
        db.commit()
        db.refresh(text)
        return text

    def get_unprocessed(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Text]:
        """Получение необработанных текстов."""
        return (
            db.query(self.model)
            .filter(Text.processed_at.is_(None))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_processed(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Text]:
        """Получение обработанных текстов."""
        return (
            db.query(self.model)
            .filter(Text.processed_at.isnot(None))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_by_project(self, db: Session, *, project_id: int) -> int:
        """Подсчет текстов в проекте."""
        return db.query(self.model).filter(Text.project_id == project_id).count()

    def count_by_format(self, db: Session, *, format: str) -> int:
        """Подсчет текстов по формату."""
        return db.query(self.model).filter(Text.original_format == format).count()

    def get_with_characters(self, db: Session, *, text_id: int) -> Optional[Text]:
        """Получение текста с персонажами."""
        from app.database.models.character import Character
        return (
            db.query(Text)
            .filter(Text.id == text_id)
            .join(Character, isouter=True)
            .first()
        )

    def belongs_to_project(self, db: Session, *, text_id: int, project_id: int) -> bool:
        """Проверка принадлежности текста к проекту."""
        text = self.get(db, id=text_id)
        if not text:
            return False
        return text.project_id == project_id
    
    def belongs_to_user(self, db: Session, *, text_id: int, user_id: int) -> bool:
        """Проверка принадлежности текста пользователю через проект."""
        from app.database.models.project import Project
        text = (
            db.query(Text)
            .join(Project)
            .filter(Text.id == text_id)
            .filter(Project.user_id == user_id)
            .first()
        )
        return text is not None
    
    def get_user_text(self, db: Session, *, text_id: int, user_id: int) -> Optional[Text]:
        """Получение текста пользователя с проверкой прав доступа."""
        from app.database.models.project import Project
        return (
            db.query(Text)
            .join(Project)
            .filter(Text.id == text_id)
            .filter(Project.user_id == user_id)
            .first()
        )


text = CRUDText(Text)
