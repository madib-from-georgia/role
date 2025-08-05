"""
CRUD операции для персонажей.
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from app.database.crud.base import CRUDBase
from app.database.models.character import Character
from app.database.models.checklist import ChecklistResponse
from app.schemas.character import CharacterCreate, CharacterUpdate


class CRUDCharacter(CRUDBase[Character, CharacterCreate, CharacterUpdate]):
    """CRUD операции для модели Character."""

    def get_multi_by_text(
        self, db: Session, *, text_id: int, skip: int = 0, limit: int = 100
    ) -> List[Character]:
        """Получение персонажей текста."""
        return (
            db.query(self.model)
            .filter(Character.text_id == text_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_name_and_text(
        self, db: Session, *, name: str, text_id: int
    ) -> Optional[Character]:
        """Получение персонажа по имени и тексту."""
        return (
            db.query(Character)
            .filter(Character.name == name)
            .filter(Character.text_id == text_id)
            .first()
        )

    def get_by_importance(
        self, 
        db: Session, 
        *, 
        min_score: float = 0.0, 
        max_score: float = 1.0,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Character]:
        """Получение персонажей по важности."""
        return (
            db.query(self.model)
            .filter(Character.importance_score >= min_score)
            .filter(Character.importance_score <= max_score)
            .order_by(Character.importance_score.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_main_characters(
        self, db: Session, *, text_id: int, threshold: float = 0.5
    ) -> List[Character]:
        """Получение главных персонажей (с высокой важностью)."""
        return (
            db.query(self.model)
            .filter(Character.text_id == text_id)
            .filter(Character.importance_score >= threshold)
            .order_by(Character.importance_score.desc())
            .all()
        )

    def search_by_name(
        self, db: Session, *, name_pattern: str, skip: int = 0, limit: int = 100
    ) -> List[Character]:
        """Поиск персонажей по паттерну имени."""
        return (
            db.query(self.model)
            .filter(Character.name.ilike(f"%{name_pattern}%"))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_by_text(self, db: Session, *, text_id: int) -> int:
        """Подсчет персонажей в тексте."""
        return db.query(self.model).filter(Character.text_id == text_id).count()

    def get_with_responses(self, db: Session, *, character_id: int) -> Optional[Character]:
        """Получение персонажа с ответами чеклистов."""
        from app.database.models.checklist import ChecklistResponse
        return (
            db.query(Character)
            .filter(Character.id == character_id)
            .join(ChecklistResponse, isouter=True)
            .first()
        )

    def belongs_to_text(self, db: Session, *, character_id: int, text_id: int) -> bool:
        """Проверка принадлежности персонажа к тексту."""
        character = self.get(db, id=character_id)
        if not character:
            return False
        return character.text_id == text_id

    def update_importance(
        self, db: Session, *, character_id: int, importance_score: float
    ) -> Optional[Character]:
        """Обновление важности персонажа."""
        character = self.get(db, id=character_id)
        if not character:
            return None
        
        if not (0.0 <= importance_score <= 1.0):
            raise ValueError("Importance score должен быть между 0.0 и 1.0")
        
        character.importance_score = importance_score
        db.add(character)
        db.commit()
        db.refresh(character)
        return character


character = CRUDCharacter(Character)
