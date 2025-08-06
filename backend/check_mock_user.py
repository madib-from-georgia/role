#!/usr/bin/env python3
"""
Скрипт для проверки mock пользователя в базе данных
"""

import sys
from pathlib import Path

# Добавляем корневую директорию в Python path
sys.path.append(str(Path(__file__).parent))

from sqlalchemy.orm import Session
from app.database.connection import SessionLocal
from app.services.auth import auth_service
from loguru import logger


def check_mock_user():
    """Проверяет существование mock пользователя"""
    
    db: Session = SessionLocal()
    
    try:
        # Проверяем, существует ли mock пользователь
        mock_user = auth_service.get_user_by_email(db, "dev@example.com")
        
        if mock_user:
            logger.success(f"✅ Mock пользователь найден:")
            logger.info(f"  - ID: {mock_user.id}")
            logger.info(f"  - Username: {mock_user.username}")
            logger.info(f"  - Email: {mock_user.email}")
            logger.info(f"  - Full Name: {mock_user.full_name}")
            logger.info(f"  - Is Active: {mock_user.is_active}")
            return mock_user
        else:
            logger.error("❌ Mock пользователь не найден")
            return None
            
    finally:
        db.close()


if __name__ == "__main__":
    check_mock_user() 
