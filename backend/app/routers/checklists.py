"""
Роутер для управления чеклистами.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.database.connection import get_db

router = APIRouter()


@router.get("/modules")
async def get_checklist_modules(db: Session = Depends(get_db)):
    """Получение списка всех модулей чеклистов."""
    return {"message": "Get checklist modules endpoint - в разработке"}


@router.get("/modules/{module_id}")
async def get_checklist_module(module_id: str, db: Session = Depends(get_db)):
    """Получение конкретного модуля чеклиста."""
    return {"message": f"Get checklist module {module_id} endpoint - в разработке"}


@router.get("/modules/{module_id}/questions")
async def get_module_questions(module_id: str, db: Session = Depends(get_db)):
    """Получение вопросов модуля."""
    return {"message": f"Get questions for module {module_id} endpoint - в разработке"}