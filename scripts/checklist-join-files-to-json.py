#!/usr/bin/env python3
"""
Скрипт для восстановления исходного JSON файла из дерева файлов.
"""

import json
import os
from pathlib import Path
import argparse


def load_json_file(file_path: Path) -> dict:
    """Загружает JSON файл."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def rebuild_answers(question_dir: Path, answer_refs: list) -> list:
    """Восстанавливает ответы из файлов."""
    answers = []
    for answer_ref in answer_refs:
        answer_path = question_dir / answer_ref
        if answer_path.exists():
            answer_data = load_json_file(answer_path)
            # Удаляем служебные поля
            if 'type' in answer_data:
                del answer_data['type']
            # Удаляем title если он None (не был в исходных данных)
            if answer_data.get('title') is None:
                answer_data.pop('title', None)
            # Сохраняем поле exercise даже если оно пустое
            # (не удаляем его)
            answers.append(answer_data)
    return answers


def rebuild_questions(group_dir: Path, question_refs: list) -> list:
    """Восстанавливает вопросы из файлов."""
    questions = []
    for question_ref in question_refs:
        question_path = group_dir / question_ref
        if question_path.exists():
            question_data = load_json_file(question_path)
            
            # Восстанавливаем ответы
            if 'children' in question_data:
                question_dir = question_path.parent
                answers = rebuild_answers(question_dir, question_data['children'])
                question_data['answers'] = answers
                del question_data['children']
            
            # Удаляем служебные поля
            if 'type' in question_data:
                del question_data['type']
            # Удаляем title если он None
            if question_data.get('title') is None:
                question_data.pop('title', None)
            
            questions.append(question_data)
    return questions


def rebuild_question_groups(subsection_dir: Path, group_refs: list) -> list:
    """Восстанавливает группы вопросов из файлов."""
    groups = []
    for group_ref in group_refs:
        group_path = subsection_dir / group_ref
        if group_path.exists():
            group_data = load_json_file(group_path)
            
            # Восстанавливаем вопросы
            if 'children' in group_data:
                group_dir = group_path.parent
                questions = rebuild_questions(group_dir, group_data['children'])
                group_data['questions'] = questions
                del group_data['children']
            
            # Удаляем служебные поля
            if 'type' in group_data:
                del group_data['type']
            # Удаляем title если он None
            if group_data.get('title') is None:
                group_data.pop('title', None)
            
            groups.append(group_data)
    return groups


def rebuild_subsections(section_dir: Path, subsection_refs: list) -> list:
    """Восстанавливает подсекции из файлов."""
    subsections = []
    for subsection_ref in subsection_refs:
        subsection_path = section_dir / subsection_ref
        if subsection_path.exists():
            subsection_data = load_json_file(subsection_path)
            
            # Восстанавливаем группы вопросов
            if 'children' in subsection_data:
                subsection_dir = subsection_path.parent
                groups = rebuild_question_groups(subsection_dir, subsection_data['children'])
                subsection_data['questionGroups'] = groups
                del subsection_data['children']
            
            # Удаляем служебные поля
            if 'type' in subsection_data:
                del subsection_data['type']
            # Удаляем title если он None
            if subsection_data.get('title') is None:
                subsection_data.pop('title', None)
            
            subsections.append(subsection_data)
    return subsections


def rebuild_sections(portrait_dir: Path, section_refs: list) -> list:
    """Восстанавливает секции из файлов."""
    sections = []
    for section_ref in section_refs:
        section_path = portrait_dir / section_ref
        if section_path.exists():
            section_data = load_json_file(section_path)
            
            # Восстанавливаем подсекции
            if 'children' in section_data:
                section_dir = section_path.parent
                subsections = rebuild_subsections(section_dir, section_data['children'])
                section_data['subsections'] = subsections
                del section_data['children']
            
            # Удаляем служебные поля
            if 'type' in section_data:
                del section_data['type']
            # Удаляем title если он None
            if section_data.get('title') is None:
                section_data.pop('title', None)
            
            sections.append(section_data)
    return sections


def rebuild_json_tree(tree_dir: str, output_file: str) -> None:
    """Восстанавливает JSON файл из дерева файлов."""
    
    tree_path = Path(tree_dir)
    
    # Читаем индексный файл
    index_path = tree_path / "index.json"
    if not index_path.exists():
        print(f"Ошибка: Индексный файл {index_path} не найден")
        return
    
    index_data = load_json_file(index_path)
    root_file = index_data.get('root')
    
    if not root_file:
        print("Ошибка: В индексном файле не указан корневой файл")
        return
    
    # Загружаем корневой файл
    root_path = tree_path / root_file
    if not root_path.exists():
        print(f"Ошибка: Корневой файл {root_path} не найден")
        return
    
    portrait_data = load_json_file(root_path)
    
    # Восстанавливаем секции
    if 'children' in portrait_data:
        portrait_dir = root_path.parent
        sections = rebuild_sections(portrait_dir, portrait_data['children'])
        portrait_data['sections'] = sections
        del portrait_data['children']
    
    # Удаляем служебные поля
    if 'type' in portrait_data:
        del portrait_data['type']
    # Удаляем title если он None
    if portrait_data.get('title') is None:
        portrait_data.pop('title', None)
    
    # Сохраняем восстановленный JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(portrait_data, f, ensure_ascii=False, indent=2)
    
    print(f"JSON файл успешно восстановлен: {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Восстановление JSON файла из дерева файлов")
    parser.add_argument("tree_dir", help="Директория с деревом файлов")
    parser.add_argument("output_file", help="Выходной JSON файл")
    
    args = parser.parse_args()
    
    rebuild_json_tree(args.tree_dir, args.output_file)
