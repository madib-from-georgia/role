"""
Скрипт для создания тестового пользователя
"""

import sys
from pathlib import Path

# Добавляем корневую директорию в Python path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.database.connection import SessionLocal
from app.database.models.user import User
from app.services.auth import get_password_hash
from loguru import logger


def create_test_user():
    """Создает тестового пользователя"""
    
    db: Session = SessionLocal()
    
    try:
        # Проверяем, существует ли уже пользователь
        existing_user = db.query(User).filter(User.username == "testuser").first()
        if existing_user:
            logger.info(f"Пользователь уже существует: {existing_user.username} (ID: {existing_user.id})")
            return existing_user
        
        # Создаем нового пользователя
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "hashed_password": get_password_hash("testpass123"),
            "is_active": True
        }
        
        user = User(**user_data)
        db.add(user)
        db.commit()
        db.refresh(user)
        
        logger.success(f"Создан тестовый пользователь: {user.username} (ID: {user.id})")
        return user
        
    except Exception as e:
        logger.error(f"Ошибка создания пользователя: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_test_user() 
