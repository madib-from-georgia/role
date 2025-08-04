#!/usr/bin/env python3
"""
Консольный скрипт для просмотра проектов пользователя.

Usage:
    python show_user_projects.py <email_or_username>
    python show_user_projects.py makishvili@yandex.ru
    python show_user_projects.py makishvili
"""

import sys
import asyncio
from pathlib import Path

# Добавляем путь к приложению
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.database.connection import SessionLocal

# Импортируем все модели для правильной инициализации связей
from app.database.models import user, project, text, character, token, checklist
from app.database.models.user import User
from app.database.models.project import Project
from app.database.models.text import Text
from app.database.models.character import Character


def get_user_by_email_or_username(db: Session, identifier: str) -> User | None:
    """Получение пользователя по email или username."""
    # Сначала пробуем найти по email
    user = db.query(User).filter(User.email == identifier).first()
    if user:
        return user
    
    # Если не найден, пробуем по username
    user = db.query(User).filter(User.username == identifier).first()
    return user


def show_user_projects(identifier: str):
    """Показывает все проекты пользователя."""
    db = SessionLocal()
    
    try:
        # Ищем пользователя
        user = get_user_by_email_or_username(db, identifier)
        if not user:
            print(f"❌ Пользователь с email или username '{identifier}' не найден")
            return
        
        print(f"👤 Пользователь: {user.username} ({user.email})")
        print(f"📅 Зарегистрирован: {user.created_at.strftime('%d.%m.%Y %H:%M')}")
        print(f"✅ Активен: {'Да' if user.is_active else 'Нет'}")
        print()
        
        # Получаем проекты пользователя
        projects = db.query(Project).filter(Project.user_id == user.id).order_by(Project.created_at.desc()).all()
        
        if not projects:
            print("📁 У пользователя нет проектов")
            return
        
        print(f"📂 Проекты пользователя ({len(projects)}):")
        print("=" * 80)
        
        for i, project in enumerate(projects, 1):
            print(f"{i}. 📁 {project.title}")
            if project.description:
                print(f"   📝 {project.description}")
            print(f"   🆔 ID: {project.id}")
            print(f"   📅 Создан: {project.created_at.strftime('%d.%m.%Y %H:%M')}")
            print(f"   🔄 Обновлен: {project.updated_at.strftime('%d.%m.%Y %H:%M')}")
            
            # Получаем тексты проекта
            texts = db.query(Text).filter(Text.project_id == project.id).all()
            print(f"   📚 Текстов: {len(texts)}")
            
            if texts:
                processed_texts = [t for t in texts if t.processed_at]
                unprocessed_texts = [t for t in texts if not t.processed_at]
                
                print(f"      ✅ Обработано: {len(processed_texts)}")
                print(f"      ⏳ В ожидании: {len(unprocessed_texts)}")
                
                # Показываем файлы
                for text in texts:
                    status = "✅" if text.processed_at else "⏳"
                    print(f"      {status} {text.filename} ({text.original_format})")
                    
                    # Показываем персонажей для обработанных текстов
                    if text.processed_at:
                        characters = db.query(Character).filter(Character.text_id == text.id).all()
                        if characters:
                            print(f"         👥 Персонажей: {len(characters)}")
                            for char in characters[:3]:  # Показываем первых 3
                                importance = f" ({int(char.importance_score * 100)}%)" if char.importance_score else ""
                                print(f"         • {char.name}{importance}")
                            if len(characters) > 3:
                                print(f"         • ... и еще {len(characters) - 3}")
            print()
        
        # Общая статистика
        total_texts = sum(len(db.query(Text).filter(Text.project_id == p.id).all()) for p in projects)
        total_processed = sum(len([t for t in db.query(Text).filter(Text.project_id == p.id).all() if t.processed_at]) for p in projects)
        total_characters = sum(len(db.query(Character).join(Text).filter(Text.project_id == p.id).all()) for p in projects)
        
        print("📊 Общая статистика:")
        print(f"   📁 Проектов: {len(projects)}")
        print(f"   📚 Всего текстов: {total_texts}")
        print(f"   ✅ Обработано текстов: {total_processed}")
        print(f"   👥 Всего персонажей: {total_characters}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        db.close()


def main():
    """Главная функция."""
    if len(sys.argv) != 2:
        print("Usage: python show_user_projects.py <email_or_username>")
        print("Example: python show_user_projects.py makishvili@yandex.ru")
        print("Example: python show_user_projects.py makishvili")
        sys.exit(1)
    
    identifier = sys.argv[1]
    show_user_projects(identifier)


if __name__ == "__main__":
    main()
