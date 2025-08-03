"""
Базовый CRUD класс для всех моделей.
"""

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database.models.base import BaseModel as DBBaseModel

ModelType = TypeVar("ModelType", bound=DBBaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Базовый CRUD класс с основными операциями Create, Read, Update, Delete.
    """

    def __init__(self, model: Type[ModelType]):
        """
        CRUD объект с дефолтными методами для Create, Read, Update, Delete (CRUD).
        
        **Параметры**
        
        * `model`: SQLAlchemy модель
        * `schema`: Pydantic схема модели
        """
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """Получение записи по ID."""
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """Получение списка записей с пагинацией."""
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """Создание новой записи."""
        if isinstance(obj_in, dict):
            obj_in_data = obj_in
        else:
            obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        try:
            db.commit()
            db.refresh(db_obj)
        except IntegrityError as e:
            db.rollback()
            raise ValueError(f"Ошибка создания записи: {str(e)}")
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """Обновление существующей записи."""
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        
        db.add(db_obj)
        try:
            db.commit()
            db.refresh(db_obj)
        except IntegrityError as e:
            db.rollback()
            raise ValueError(f"Ошибка обновления записи: {str(e)}")
        return db_obj

    def remove(self, db: Session, *, id: int) -> ModelType:
        """Удаление записи по ID."""
        obj = db.query(self.model).get(id)
        if not obj:
            raise ValueError(f"Запись с ID {id} не найдена")
        db.delete(obj)
        db.commit()
        return obj

    def count(self, db: Session) -> int:
        """Подсчет общего количества записей."""
        return db.query(self.model).count()

    def exists(self, db: Session, *, id: int) -> bool:
        """Проверка существования записи по ID."""
        return db.query(self.model).filter(self.model.id == id).first() is not None

    def get_by_field(self, db: Session, *, field: str, value: Any) -> Optional[ModelType]:
        """Получение записи по значению поля."""
        return db.query(self.model).filter(getattr(self.model, field) == value).first()

    def get_multi_by_field(
        self, 
        db: Session, 
        *, 
        field: str, 
        value: Any, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[ModelType]:
        """Получение списка записей по значению поля."""
        return (
            db.query(self.model)
            .filter(getattr(self.model, field) == value)
            .offset(skip)
            .limit(limit)
            .all()
        )
