"""
API endpoints для управления проектами.
"""

from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import traceback

from app.dependencies.auth import get_db, get_current_active_user
from app.database.crud import project as project_crud, text as text_crud
from app.database.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate, Project
from app.schemas.text import TextCreate
from app.services.file_processor import file_processor
from app.services.nlp_processor import get_nlp_processor


router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("/", response_model=List[Project])
async def get_user_projects(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Получение всех проектов текущего пользователя.

    Требует авторизации.
    """
    projects = project_crud.get_user_projects(db, user_id=current_user.id)
    return projects


@router.post("/", response_model=Project, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Создание нового проекта.

    - **title**: Название проекта (обязательно)
    - **description**: Описание проекта (опционально)

    Требует авторизации.
    """
    try:
        # Используем метод create_with_owner для установки владельца
        created_project = project_crud.create_with_owner(
            db, obj_in=project_data, owner_id=current_user.id
        )
        return created_project

    except Exception as e:
        print(f"Project creation error: {str(e)}")  # Debug logging
        import traceback
        traceback.print_exc()  # Debug traceback
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при создании проекта: {str(e)}"
        )


@router.get("/{project_id}", response_model=Project)
async def get_project(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Получение конкретного проекта по ID.

    Требует авторизации. Пользователь может получить только свои проекты.
    """
    project = project_crud.get(db, id=project_id)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Проект не найден"
        )

    # Проверяем права доступа - пользователь может видеть только свои проекты
    if project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет прав доступа к этому проекту"
        )

    return project


@router.put("/{project_id}", response_model=Project)
async def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Обновление проекта.

    - **title**: Новое название проекта (опционально)
    - **description**: Новое описание проекта (опционально)

    Требует авторизации. Пользователь может обновлять только свои проекты.
    """
    # Получаем существующий проект
    project = project_crud.get(db, id=project_id)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Проект не найден"
        )

    # Проверяем права доступа
    if project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет прав доступа к этому проекту"
        )

    try:
        updated_project = project_crud.update(db, db_obj=project, obj_in=project_update)
        return updated_project

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обновлении проекта: {str(e)}"
        )


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Удаление проекта.

    Требует авторизации. Пользователь может удалять только свои проекты.

    ВНИМАНИЕ: Это действие необратимо. Все тексты и персонажи проекта также будут удалены.
    """
    # Получаем существующий проект
    project = project_crud.get(db, id=project_id)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Проект не найден"
        )

    # Проверяем права доступа
    if project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет прав доступа к этому проекту"
        )

    try:
        project_crud.remove(db, id=project_id)
        # Возвращаем 204 No Content при успешном удалении

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при удалении проекта: {str(e)}"
        )


@router.get("/{project_id}/texts", response_model=List[dict])
async def get_project_texts(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Получение списка текстов проекта.

    Требует авторизации. Пользователь может видеть тексты только своих проектов.
    """
    # Сначала проверяем, что проект существует и принадлежит пользователю
    project = project_crud.get(db, id=project_id)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Проект не найден"
        )

    if project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет прав доступа к этому проекту"
        )

    # Получаем тексты проекта через связанные объекты
    return [
        {
            "id": text.id,
            "filename": text.filename,
            "original_format": text.original_format,
            "processed_at": text.processed_at,
            "created_at": text.created_at.isoformat() if text.created_at else None,
            "content_length": len(text.content) if text.content else 0
        }
        for text in project.texts
    ]


@router.get("/{project_id}/statistics")
async def get_project_statistics(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Получение статистики проекта.

    Возвращает количество текстов, персонажей и другую аналитику.

    Требует авторизации. Пользователь может видеть статистику только своих проектов.
    """
    # Проверяем права доступа к проекту
    project = project_crud.get(db, id=project_id)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Проект не найден"
        )

    if project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет прав доступа к этому проекту"
        )

    # Собираем статистику
    texts_count = len(project.texts)
    characters_count = sum(len(text.characters) for text in project.texts)

    return {
        "project_id": project_id,
        "texts_count": texts_count,
        "characters_count": characters_count,
        "created_at": project.created_at.isoformat(),
        "updated_at": project.updated_at.isoformat()
    }


@router.post("/{project_id}/texts/upload", status_code=status.HTTP_201_CREATED)
async def upload_text_file(
    project_id: int,
    file: UploadFile = File(...),
    analyze_text: bool = True,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Загрузка и обработка текстового файла в проект.

    - **project_id**: ID проекта для загрузки файла
    - **file**: Файл для загрузки (TXT, PDF, FB2, EPUB)
    - **analyze_text**: Автоматически анализировать текст и искать персонажей (по умолчанию True)

    Поддерживаемые форматы:
    - TXT - текстовые файлы различных кодировок
    - PDF - документы PDF (извлечение текста)
    - FB2 - FictionBook 2.0 (русская художественная литература)
    - EPUB - электронные книги

    Требует авторизации. Пользователь может загружать файлы только в свои проекты.
    """
    try:
        # Получаем проект с проверкой прав доступа
        project = project_crud.get(db, id=project_id)

        if not project or not project_crud.is_owner(db, project_id=project_id, user_id=current_user.id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Проект не найден или нет прав доступа"
            )

        # Обрабатываем файл
        print(f"🔍 Processing file: {file.filename} for project {project_id}")
        processed_data = await file_processor.process_file(file)

        # Создаем запись в базе данных
        text_data = TextCreate(
            filename=processed_data['filename'],
            original_format=processed_data['original_format'],
            content=processed_data['content'],
            project_id=project_id
        )

        # Сохраняем в БД
        created_text = text_crud.create(db, obj_in=text_data)

        # Сохраняем метаданные если есть
        if processed_data.get('metadata'):
            update_data = {"file_metadata": processed_data['metadata']}
            text_crud.update(db, db_obj=created_text, obj_in=update_data)

        print(f"✅ File {file.filename} processed successfully, text_id: {created_text.id}")

        # Запускаем автоматическую NLP обработку для поиска персонажей, только если analyze_text=True
        if analyze_text:
            try:
                print(f"🧠 Starting NLP processing for text_id: {created_text.id}")
                nlp_processor = get_nlp_processor()
                nlp_result = await nlp_processor.process_text(
                    text_id=created_text.id,
                    db=db,
                    force_reprocess=False
                )

                # Отмечаем текст как обработанный
                text_crud.mark_as_processed(db, text_id=created_text.id)

                print(f"🎭 Found {len(nlp_result.characters)} characters in {file.filename}")

            except Exception as nlp_error:
                # Логируем ошибку NLP, но не прерываем загрузку файла
                print(f"⚠️ NLP processing failed for {file.filename}: {str(nlp_error)}")
                traceback.print_exc()
        else:
            print(f"⏭️ Skipping NLP analysis for {file.filename} (analyze_text=False)")

        return {
            "success": True,
            "message": "Файл успешно загружен и обработан",
            "text_id": created_text.id,
            "filename": created_text.filename,
            "format": created_text.original_format,
            "content_length": len(created_text.content) if created_text.content else 0,
            "metadata": processed_data.get('metadata', {}),
            "created_at": created_text.created_at.isoformat()
        }

    except ValueError as e:
        # Ошибки валидации файла
        print(f"❌ File validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except Exception as e:
        # Общие ошибки обработки
        print(f"❌ File processing error: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обработке файла: {str(e)}"
        )
