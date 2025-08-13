#!/usr/bin/env python3
"""
Скрипт для обновления пола существующих персонажей в базе данных.
"""

import sys
import os
from sqlalchemy.orm import Session

# Добавляем путь к приложению
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.database.connection import get_db
from app.database.crud import character as character_crud
from app.services.nlp.gender_detector import GenderDetector
from app.database.models.character import GenderEnum


def update_characters_gender():
    """Обновляет пол для всех существующих персонажей."""
    print("🔄 Начинаю обновление пола существующих персонажей...")
    
    # Получаем сессию базы данных
    db_gen = get_db()
    db: Session = next(db_gen)
    
    try:
        # Создаем детектор пола
        gender_detector = GenderDetector()
        
        # Получаем всех персонажей с null gender
        characters = db.query(character_crud.model).filter(
            character_crud.model.gender.is_(None)
        ).all()
        
        print(f"📊 Найдено {len(characters)} персонажей без определенного пола")
        
        updated_count = 0
        
        for character in characters:
            try:
                # Извлекаем описание из speech_attribution
                description = None
                if character.speech_attribution and isinstance(character.speech_attribution, dict):
                    description = character.speech_attribution.get('description')
                
                # Определяем пол
                gender = gender_detector.detect_gender(
                    name=character.name,
                    description=description
                )
                
                # Конвертируем в enum базы данных
                if gender.value == "male":
                    db_gender = GenderEnum.MALE
                elif gender.value == "female":
                    db_gender = GenderEnum.FEMALE
                else:
                    db_gender = GenderEnum.UNKNOWN
                
                # Обновляем персонажа
                character.gender = db_gender
                db.commit()
                
                confidence = gender_detector.get_confidence_score(character.name, description)
                print(f"✅ {character.name}: {gender.value} (уверенность: {confidence:.2f})")
                
                updated_count += 1
                
            except Exception as e:
                print(f"❌ Ошибка при обновлении персонажа '{character.name}': {e}")
                db.rollback()
        
        print(f"\n🎉 Обновлено {updated_count} персонажей")
        
        # Проверяем результат
        remaining_null = db.query(character_crud.model).filter(
            character_crud.model.gender.is_(None)
        ).count()
        
        print(f"📊 Персонажей без пола: {remaining_null}")
        
        if remaining_null == 0:
            print("✨ Все персонажи успешно обновлены!")
        
        return updated_count
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        db.rollback()
        return 0
    finally:
        db.close()


def main():
    """Основная функция."""
    print("🚀 Скрипт обновления пола персонажей")
    print("=" * 50)
    
    try:
        updated = update_characters_gender()
        
        if updated > 0:
            print(f"\n✅ Успешно обновлено {updated} персонажей")
            return 0
        else:
            print("\n⚠️  Персонажи не были обновлены")
            return 1
            
    except Exception as e:
        print(f"\n❌ Ошибка выполнения скрипта: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)