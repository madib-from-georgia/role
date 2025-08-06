#!/usr/bin/env python3
"""
Скрипт для полной очистки базы данных
Удаляет все данные из всех таблиц
"""

import os
import sys
from pathlib import Path

# Добавляем корневую директорию в Python path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from app.config.settings import settings
from app.database.connection import Base
# Импортируем модели для регистрации в метаданных
# Импортируем модели для регистрации в метаданных
from app.database.models import user, project, character, checklist, token
from app.database.models import text as text_model

def clean_database():
    """Полная очистка базы данных"""
    
    print("🧹 Начинаю полную очистку базы данных...")
    
    # Создаем подключение к базе данных
    engine = create_engine(settings.database_url)
    
    try:
        with engine.connect() as conn:
            # Получаем список всех таблиц
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = [row[0] for row in result.fetchall()]
            
            print(f"📋 Найдено таблиц: {len(tables)}")
            for table in tables:
                print(f"  - {table}")
            
            # Отключаем проверку внешних ключей для SQLite
            conn.execute(text("PRAGMA foreign_keys=OFF"))
            
            # Очищаем каждую таблицу
            for table in tables:
                if table != 'sqlite_sequence':  # Пропускаем системную таблицу
                    print(f"🗑️  Очищаю таблицу: {table}")
                    conn.execute(text(f"DELETE FROM {table}"))
                    # Сбрасываем автоинкремент (если таблица существует)
                    try:
                        conn.execute(text(f"DELETE FROM sqlite_sequence WHERE name='{table}'"))
                    except Exception:
                        pass  # Игнорируем ошибку, если таблица не существует
            
            # Включаем обратно проверку внешних ключей
            conn.execute(text("PRAGMA foreign_keys=ON"))
            
            # Фиксируем изменения
            conn.commit()
            
            print("✅ База данных успешно очищена!")
            
            # Проверяем, что таблицы действительно пустые
            print("\n📊 Проверка очистки:")
            for table in tables:
                if table != 'sqlite_sequence':
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.fetchone()[0]
                    print(f"  - {table}: {count} записей")
            
    except Exception as e:
        print(f"❌ Ошибка при очистке базы данных: {e}")
        return False
    
    finally:
        engine.dispose()
    
    return True

def reset_autoincrement():
    """Сброс автоинкремента для всех таблиц"""
    
    print("\n🔄 Сброс автоинкремента...")
    
    engine = create_engine(settings.database_url)
    
    try:
        with engine.connect() as conn:
            # Получаем список таблиц
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = [row[0] for row in result.fetchall()]
            
            for table in tables:
                if table != 'sqlite_sequence':
                    print(f"  - Сбрасываю автоинкремент для {table}")
                    try:
                        conn.execute(text(f"DELETE FROM sqlite_sequence WHERE name='{table}'"))
                    except Exception:
                        pass  # Игнорируем ошибку, если таблица не существует
            
            conn.commit()
            print("✅ Автоинкремент сброшен!")
            
    except Exception as e:
        print(f"❌ Ошибка при сбросе автоинкремента: {e}")
        return False
    
    finally:
        engine.dispose()
    
    return True

def main():
    """Основная функция"""
    
    print("=" * 60)
    print("🗄️  СКРИПТ ПОЛНОЙ ОЧИСТКИ БАЗЫ ДАННЫХ")
    print("=" * 60)
    
    # Запрашиваем подтверждение
    response = input("\n⚠️  ВНИМАНИЕ! Это действие удалит ВСЕ данные из базы данных!\n"
                    "Это действие НЕОБРАТИМО!\n\n"
                    "Введите 'YES' для подтверждения: ")
    
    if response != 'YES':
        print("❌ Операция отменена пользователем")
        return
    
    print("\n🚨 Начинаю полную очистку базы данных...")
    
    # Очищаем базу данных
    if clean_database():
        # Сбрасываем автоинкремент
        reset_autoincrement()
        
        print("\n" + "=" * 60)
        print("✅ БАЗА ДАННЫХ ПОЛНОСТЬЮ ОЧИЩЕНА!")
        print("=" * 60)
        print("\n📝 Что было сделано:")
        print("  - Удалены все записи из всех таблиц")
        print("  - Сброшен автоинкремент для всех таблиц")
        print("  - База данных готова к новому использованию")
        print("\n💡 Теперь можно:")
        print("  - Запустить миграции: alembic upgrade head")
        print("  - Создать нового пользователя")
        print("  - Загрузить новые данные")
    else:
        print("\n❌ Ошибка при очистке базы данных")

if __name__ == "__main__":
    main() 
