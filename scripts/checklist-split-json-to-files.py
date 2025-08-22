#!/usr/bin/env python3
"""
Скрипт для разделения большого JSON файла с иерархической структурой
на множество маленьких файлов, сохраняя отношения в виде дерева на файловой системе.

Структура:
Portrait -> Section -> Subsection -> QuestionGroup -> Question -> Answer

Использование:
python split_json_tree.py input.json output_directory
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any
import argparse


def sanitize_filename(name: str) -> str:
    """Очищает строку для использования в качестве имени файла/папки."""
    # Заменяем недопустимые символы на подчеркивания
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '_')
    
    # Убираем лишние пробелы и заменяем их на подчеркивания
    name = name.strip().replace(' ', '_')
    
    # Ограничиваем длину
    if len(name) > 50:
        name = name[:50]
    
    return name


def create_reference_file(file_path: Path, data: Dict[str, Any], children_refs: List[str] = None) -> None:
    """Создает файл с основными данными и ссылками на дочерние элементы."""
    reference_data = {
        'id': data.get('id'),
        'type': data.get('type', 'unknown')
    }
    
    # Добавляем title только если он существует и не None
    if data.get('title') is not None:
        reference_data['title'] = data['title']
    
    # Добавляем children только если они есть
    if children_refs:
        reference_data['children'] = children_refs
    
    # Добавляем специфичные поля для каждого типа
    if 'hint' in data:
        reference_data['hint'] = data['hint']
    if 'exercise' in data:
        reference_data['exercise'] = data['exercise']
    if 'value' in data:
        reference_data['value'] = data['value']
    if 'exportedValue' in data:
        reference_data['exportedValue'] = data['exportedValue']
    if 'answerType' in data:
        reference_data['answerType'] = data['answerType']
    if 'source' in data:
        reference_data['source'] = data['source']
    if 'answers' in data:
        reference_data['answers'] = data['answers']
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(reference_data, f, ensure_ascii=False, indent=2)


def process_questions(questions: List[Dict], group_dir: Path) -> List[str]:
    """Обрабатывает вопросы и создает файлы для каждого вопроса."""
    question_refs = []
    
    for question in questions:
        question_id = question.get('id', 'unknown')
        question_dir = group_dir / sanitize_filename(question_id)
        question_dir.mkdir(exist_ok=True)
        
        # Создаем файл вопроса с ответами внутри
        question_file = question_dir / "question.json"
        question_data = {**question, 'type': 'question'}
        # Оставляем answers в файле вопроса (не удаляем)
        
        create_reference_file(question_file, question_data)
        question_refs.append(f"{sanitize_filename(question_id)}/question.json")
    
    return question_refs


def process_question_groups(question_groups: List[Dict], subsection_dir: Path) -> List[str]:
    """Обрабатывает группы вопросов и создает папки для каждой группы."""
    group_refs = []
    
    for group in question_groups:
        group_id = group.get('id', 'unknown')
        group_dir = subsection_dir / sanitize_filename(group_id)
        group_dir.mkdir(exist_ok=True)
        
        # Обрабатываем вопросы
        question_refs = []
        if 'questions' in group:
            question_refs = process_questions(group['questions'], group_dir)
        
        # Создаем файл группы
        group_file = group_dir / "group.json"
        group_data = {**group, 'type': 'question_group'}
        # Удаляем questions из основного файла
        if 'questions' in group_data:
            del group_data['questions']
        
        create_reference_file(group_file, group_data, question_refs)
        group_refs.append(f"{sanitize_filename(group_id)}/group.json")
    
    return group_refs


def process_subsections(subsections: List[Dict], section_dir: Path) -> List[str]:
    """Обрабатывает подсекции и создает папки для каждой подсекции."""
    subsection_refs = []
    
    for subsection in subsections:
        subsection_id = subsection.get('id', 'unknown')
        subsection_dir = section_dir / sanitize_filename(subsection_id)
        subsection_dir.mkdir(exist_ok=True)
        
        # Обрабатываем группы вопросов
        group_refs = []
        if 'questionGroups' in subsection:
            group_refs = process_question_groups(subsection['questionGroups'], subsection_dir)
        
        # Создаем файл подсекции
        subsection_file = subsection_dir / "subsection.json"
        subsection_data = {**subsection, 'type': 'subsection'}
        # Удаляем questionGroups из основного файла
        if 'questionGroups' in subsection_data:
            del subsection_data['questionGroups']
        
        create_reference_file(subsection_file, subsection_data, group_refs)
        subsection_refs.append(f"{sanitize_filename(subsection_id)}/subsection.json")
    
    return subsection_refs


def process_sections(sections: List[Dict], portrait_dir: Path) -> List[str]:
    """Обрабатывает секции и создает папки для каждой секции."""
    section_refs = []
    
    for section in sections:
        section_id = section.get('id', 'unknown')
        section_dir = portrait_dir / sanitize_filename(section_id)
        section_dir.mkdir(exist_ok=True)
        
        # Обрабатываем подсекции
        subsection_refs = []
        if 'subsections' in section:
            subsection_refs = process_subsections(section['subsections'], section_dir)
        
        # Создаем файл секции
        section_file = section_dir / "section.json"
        section_data = {**section, 'type': 'section'}
        # Удаляем subsections из основного файла
        if 'subsections' in section_data:
            del section_data['subsections']
        
        create_reference_file(section_file, section_data, subsection_refs)
        section_refs.append(f"{sanitize_filename(section_id)}/section.json")
    
    return section_refs


def split_json_tree(input_file: str, output_dir: str) -> None:
    """Основная функция для разделения JSON файла на дерево файлов."""
    
    # Читаем входной JSON файл
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Ошибка: Файл {input_file} не найден")
        return
    except json.JSONDecodeError as e:
        print(f"Ошибка при чтении JSON: {e}")
        return
    
    # Создаем выходную директорию
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Обрабатываем портрет (корневой элемент)
    portrait_id = data.get('id', 'unknown')
    portrait_dir = output_path / sanitize_filename(portrait_id)
    portrait_dir.mkdir(exist_ok=True)
    
    # Обрабатываем секции
    section_refs = []
    if 'sections' in data:
        section_refs = process_sections(data['sections'], portrait_dir)
    
    # Создаем корневой файл портрета
    portrait_file = portrait_dir / "portrait.json"
    portrait_data = {**data, 'type': 'portrait'}
    # Удаляем sections из основного файла
    if 'sections' in portrait_data:
        del portrait_data['sections']
    
    create_reference_file(portrait_file, portrait_data, section_refs)
    
    # Создаем индексный файл в корне
    index_file = output_path / "index.json"
    index_data = {
        'root': f"{sanitize_filename(portrait_id)}/portrait.json",
        'created_at': str(Path(input_file).stat().st_mtime),
        'source_file': input_file,
        'structure': 'portrait -> section -> subsection -> question_group -> question -> answer'
    }
    
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)
    
    print(f"JSON файл успешно разделен на дерево файлов в директории: {output_dir}")
    print(f"Корневой файл: {portrait_dir}/portrait.json")
    print(f"Индексный файл: {output_path}/index.json")
    print(f"Для восстановления используйте: npm run checklist-join-files-to-json {output_dir} output.json")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Разделение JSON файла на дерево файлов")
    parser.add_argument("input_file", help="Входной JSON файл")
    parser.add_argument("output_dir", help="Выходная директория")
    
    args = parser.parse_args()
    
    split_json_tree(args.input_file, args.output_dir)
