#!/usr/bin/env python3
"""
Утилита для просмотра JSON логов NLP анализа
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from loguru import logger

def view_latest_logs():
    """Просмотр последних логов"""
    
    logs_dir = Path(__file__).parent.parent / "logs"
    
    if not logs_dir.exists():
        logger.error(f"Папка логов не найдена: {logs_dir}")
        return
    
    print("=" * 60)
    print("📊 NLP Analysis Logs Viewer")
    print("=" * 60)
    
    # Проверяем latest директорию
    latest_dir = logs_dir / "latest"
    if latest_dir.exists():
        print(f"\n📁 Latest Results ({latest_dir}):")
        
        latest_global = latest_dir / "latest.json"
        if latest_global.exists():
            print(f"\n🔥 Самый последний анализ:")
            show_analysis_summary(latest_global)
        
        # Показываем все latest файлы
        latest_files = sorted(latest_dir.glob("*_latest.json"))
        if latest_files:
            print(f"\n📚 Последние результаты по книгам:")
            for file in latest_files:
                book_name = file.stem.replace("_latest", "")
                print(f"\n📖 {book_name}:")
                show_analysis_summary(file)
    
    # Показываем структуру всех папок
    print(f"\n📂 Все папки с логами:")
    book_dirs = [d for d in logs_dir.iterdir() if d.is_dir() and d.name != "latest"]
    
    for book_dir in sorted(book_dirs):
        print(f"\n📁 {book_dir.name}/")
        
        # Показываем все файлы в папке
        json_files = sorted(book_dir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)
        
        for i, file in enumerate(json_files):
            file_time = datetime.fromtimestamp(file.stat().st_mtime)
            prefix = "  🔥" if file.name.endswith("_latest.json") else "  📄"
            print(f"{prefix} {file.name} ({file_time.strftime('%Y-%m-%d %H:%M:%S')})")
            
            # Для latest файла показываем краткую информацию
            if file.name.endswith("_latest.json"):
                show_analysis_summary(file, indent="      ")

def show_analysis_summary(file_path: Path, indent: str = "    "):
    """Показать краткую информацию об анализе"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        metadata = data.get("metadata", {})
        stats = data.get("extraction_stats", {})
        characters = data.get("characters", [])
        
        print(f"{indent}📄 Файл: {metadata.get('filename', 'Unknown')}")
        print(f"{indent}⏱️  Время: {metadata.get('timestamp', 'Unknown')}")
        print(f"{indent}🎭 Персонажей: {len(characters)}")
        print(f"{indent}📊 Метод: {stats.get('method_used', 'Unknown')}")
        print(f"{indent}⚡ Время обработки: {metadata.get('processing_time', 0):.2f}s")
        
        if characters:
            # Показываем топ-3 персонажей по важности
            top_chars = sorted(characters, key=lambda x: x.get('importance_score', 0), reverse=True)[:3]
            print(f"{indent}🌟 Топ персонажи:")
            for char in top_chars:
                score = char.get('importance_score', 0)
                name = char.get('name', 'Unknown')
                print(f"{indent}   • {name} ({score:.2f})")
        
    except Exception as e:
        print(f"{indent}❌ Ошибка чтения файла: {e}")

def view_specific_analysis(book_name: str):
    """Просмотр анализа конкретной книги"""
    
    logs_dir = Path(__file__).parent.parent / "logs"
    book_dir = logs_dir / book_name
    
    if not book_dir.exists():
        logger.error(f"Папка для книги '{book_name}' не найдена")
        available = [d.name for d in logs_dir.iterdir() if d.is_dir() and d.name != "latest"]
        if available:
            print(f"Доступные книги: {', '.join(available)}")
        return
    
    print(f"📖 Детальный просмотр анализа: {book_name}")
    print("=" * 60)
    
    latest_file = book_dir / "nlp_result_latest.json"
    if latest_file.exists():
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Показываем полную информацию
        print("📊 Метаданные:")
        for key, value in data.get("metadata", {}).items():
            print(f"  {key}: {value}")
        
        print("\n📈 Статистика извлечения:")
        for key, value in data.get("extraction_stats", {}).items():
            print(f"  {key}: {value}")
        
        print(f"\n🎭 Персонажи ({len(data.get('characters', []))}):")
        for char in data.get("characters", []):
            name = char.get('name', 'Unknown')
            score = char.get('importance_score', 0)
            mentions = char.get('mentions_count', 0)
            source = char.get('source', 'Unknown')
            print(f"  • {name}")
            print(f"    Важность: {score:.2f}, Упоминаний: {mentions}, Источник: {source}")
            if char.get('description'):
                print(f"    Описание: {char['description']}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        view_specific_analysis(sys.argv[1])
    else:
        view_latest_logs()
