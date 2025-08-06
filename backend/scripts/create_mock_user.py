"""
Скрипт для создания mock пользователя в базе данных
"""

import sys
from pathlib import Path

# Добавляем корневую директорию в Python path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.database.connection import SessionLocal
from app.services.auth import auth_service
from app.schemas.user import UserCreate
from loguru import logger


def create_mock_user():
    """Создает mock пользователя в базе данных"""
    
    db: Session = SessionLocal()
    
    try:
        # Проверяем, существует ли уже mock пользователь
        existing_user = auth_service.get_user_by_email(db, "dev@example.com")
        
        if existing_user:
            logger.info(f"Mock пользователь уже существует: {existing_user.username} (ID: {existing_user.id})")
            return existing_user
        
        # Создаем mock пользователя
        mock_user_data = UserCreate(
            email="dev@example.com",
            username="dev_user",
            password="dev_password_123",
            full_name="Development User",
            is_active=True
        )
        
        created_user = auth_service.register_user(db, mock_user_data)
        
        logger.success(f"Mock пользователь создан: {created_user.username} (ID: {created_user.id})")
        logger.info(f"Email: {created_user.email}")
        logger.info(f"Username: {created_user.username}")
        
        return created_user
        
    except Exception as e:
        logger.error(f"Ошибка создания mock пользователя: {e}")
        raise
    finally:
        db.close()


def ensure_mock_user_exists():
    """Проверяет и создает mock пользователя если его нет"""
    
    db: Session = SessionLocal()
    
    try:
        # Проверяем, существует ли mock пользователь
        existing_user = auth_service.get_user_by_email(db, "dev@example.com")
        
        if existing_user:
            logger.info(f"Mock пользователь найден: {existing_user.username} (ID: {existing_user.id})")
            return existing_user
        else:
            logger.info("Mock пользователь не найден, создаем...")
            return create_mock_user()
            
    finally:
        db.close()


if __name__ == "__main__":
    create_mock_user() 
