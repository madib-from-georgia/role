#!/usr/bin/env python3
"""
Скрипт для полной очистки и пересоздания базы данных
Удаляет файл базы данных, создает новую и импортирует чеклисты
"""

import os
import sys
import subprocess
from pathlib import Path

# Добавляем корневую директорию в Python path
sys.path.append(str(Path(__file__).parent.parent))

def reset_database():
    """Полная очистка и пересоздание базы данных"""
    
    print("=" * 60)
    print("🗄️  ПОЛНАЯ ОЧИСТКА И ПЕРЕСОЗДАНИЕ БАЗЫ ДАННЫХ")
    print("=" * 60)
    
    # Запрашиваем подтверждение
    response = input("\n⚠️  ВНИМАНИЕ! Это действие:\n"
                    "  - Удалит файл базы данных\n"
                    "  - Создаст новую базу данных\n"
                    "  - Импортирует чеклисты\n"
                    "  - Подготовит систему к работе\n\n"
                    "Это действие НЕОБРАТИМО!\n\n"
                    "Введите 'YES' для подтверждения: ")
    
    if response != 'YES':
        print("❌ Операция отменена пользователем")
        return False
    
    print("\n🚨 Начинаю полную очистку и пересоздание базы данных...")
    
    try:
        # 1. Удаляем файл базы данных
        print("\n🗑️  Удаляю файл базы данных...")
        db_file = Path("database.db")
        if db_file.exists():
            db_file.unlink()
            print("✅ Файл базы данных удален")
        else:
            print("ℹ️  Файл базы данных не найден (уже удален)")
        
        # 2. Запускаем миграции для создания новой базы
        print("\n🔄 Создаю новую базу данных...")
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        
        if result.returncode == 0:
            print("✅ База данных создана успешно")
        else:
            print(f"❌ Ошибка при создании базы данных: {result.stderr}")
            return False
        
        # 3. Импортируем чеклисты
        print("\n📋 Импортирую чеклисты...")
        result = subprocess.run(
            ["python", "scripts/import_checklists.py"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        
        if result.returncode == 0:
            print("✅ Чеклисты импортированы успешно")
        else:
            print(f"❌ Ошибка при импорте чеклистов: {result.stderr}")
            return False
        
        # 4. Проверяем, что база данных создана
        if db_file.exists():
            print(f"✅ Файл базы данных создан: {db_file.absolute()}")
        else:
            print("❌ Файл базы данных не создан")
            return False
        
        print("\n" + "=" * 60)
        print("✅ БАЗА ДАННЫХ ПОЛНОСТЬЮ ПЕРЕСОЗДАНА!")
        print("=" * 60)
        print("\n📝 Что было сделано:")
        print("  - Удален старый файл базы данных")
        print("  - Создана новая база данных с правильной структурой")
        print("  - Импортированы все чеклисты")
        print("  - Система готова к работе")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при пересоздании базы данных: {e}")
        return False

def main():
    """Основная функция"""
    
    success = reset_database()
    
    if success:
        print("\n🎉 Система готова к работе!")
        print("\n📋 Следующие шаги:")
        print("1. Запустите приложение: npm run dev")
        print("3. Откройте http://localhost:5173 в браузере")
        print("4. Создайте нового пользователя")
    else:
        print("\n❌ Ошибка при пересоздании базы данных")
        print("Проверьте логи выше и попробуйте снова")

if __name__ == "__main__":
    main() 
