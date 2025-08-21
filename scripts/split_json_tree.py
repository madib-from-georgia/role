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
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(reference_data, f, ensure_ascii=False, indent=2)


def process_answers(answers: List[Dict], question_dir: Path) -> List[str]:
    """Обрабатывает ответы и создает файлы для каждого ответа."""
    answer_refs = []
    
    for answer in answers:
        answer_id = answer.get('id', 'unknown')
        answer_filename = f"{answer_id}.json"
        answer_path = question_dir / answer_filename
        
        # Добавляем тип для идентификации
        answer_data = {**answer, 'type': 'answer'}
        
        create_reference_file(answer_path, answer_data)
        answer_refs.append(answer_filename)
    
    return answer_refs


def process_questions(questions: List[Dict], group_dir: Path) -> List[str]:
    """Обрабатывает вопросы и создает файлы для каждого вопроса."""
    question_refs = []
    
    for question in questions:
        question_id = question.get('id', 'unknown')
        question_dir = group_dir / sanitize_filename(question_id)
        question_dir.mkdir(exist_ok=True)
        
        # Обрабатываем ответы
        answer_refs = []
        if 'answers' in question:
            answer_refs = process_answers(question['answers'], question_dir)
        
        # Создаем файл вопроса
        question_file = question_dir / "question.json"
        question_data = {**question, 'type': 'question'}
        # Удаляем answers из основного файла, так как они теперь в отдельных файлах
        if 'answers' in question_data:
            del question_data['answers']
        
        create_reference_file(question_file, question_data, answer_refs)
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


def create_rebuild_script(output_dir: str) -> None:
    """Создает скрипт для восстановления исходного JSON из дерева файлов."""
    
    rebuild_script = '''#!/usr/bin/env python3
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
    question_groups = []
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
            
            question_groups.append(group_data)
    return question_groups


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
                question_groups = rebuild_question_groups(subsection_dir, subsection_data['children'])
                subsection_data['questionGroups'] = question_groups
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
'''
    
    rebuild_script_path = Path(output_dir) / "rebuild_json.py"
    with open(rebuild_script_path, 'w', encoding='utf-8') as f:
        f.write(rebuild_script)
    
    # Делаем скрипт исполняемым
    os.chmod(rebuild_script_path, 0o755)
    
    print(f"Создан скрипт для восстановления: {rebuild_script_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Разделение JSON файла на дерево файлов")
    parser.add_argument("input_file", help="Входной JSON файл")
    parser.add_argument("output_dir", help="Выходная директория")
    parser.add_argument("--create-rebuild-script", action="store_true", 
                       help="Создать скрипт для восстановления JSON")
    
    args = parser.parse_args()
    
    split_json_tree(args.input_file, args.output_dir)
    
    if args.create_rebuild_script:
        create_rebuild_script(args.output_dir)
