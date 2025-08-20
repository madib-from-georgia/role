import React, { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "react-query";
import { Button, Progress, Text, TextInput, Select } from "@gravity-ui/uikit";
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
} from '@dnd-kit/core';
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable';
import {
  useSortable,
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import {
  projectsApi,
  textsApi,
  charactersApi,
  checklistApi,
} from "../services/api";
import { Project } from "../../../shared/types";

// Фактический тип ответа загрузки файла от backend
interface FileUploadResponse {
  success: boolean;
  text_id: number;
  filename: string;
  format: string;
  content_length: number;
  metadata: Record<string, unknown>;
  created_at: string;
  message?: string;
}

// Фактический тип данных текста, которые возвращает API /projects/{id}/texts
interface ProjectText {
  id: number;
  filename: string;
  original_format: string;
  processed_at?: string;
  created_at: string;
}

// Интерфейс для персонажа
interface Character {
  id: number;
  name: string;
  gender?: "male" | "female" | "unknown";
  sort_order?: number;
  aliases?: string[];
  importance_score?: number;
  speech_attribution?: Record<string, unknown>;
  created_at?: string;
}

const fetchProject = async (id: string): Promise<Project> => {
  return await projectsApi.getById(id) as Project;
};

const fetchProjectTexts = async (projectId: string): Promise<ProjectText[]> => {
  return await textsApi.getByProject(projectId) as ProjectText[];
};

const uploadText = async (
  projectId: string,
  file: File
): Promise<FileUploadResponse> => {
  const formData = new FormData();
  formData.append("file", file);
  return await textsApi.upload(projectId, formData);
};

const deleteProject = async (id: string): Promise<void> => {
  await projectsApi.delete(id);
};

const fetchCharacters = async (textId: string): Promise<Character[]> => {
  return await charactersApi.getByText(textId) as Character[];
};

// Sortable компонент для @dnd-kit
const SortableCharacterItem: React.FC<{
  character: Character;
  onCharacterClick: (character: Character) => void;
  onEditCharacter: (character: Character) => void;
  onDeleteCharacter: (character: Character) => void;
  isEditing: boolean;
  editName: string;
  editGender: string;
  onEditNameChange: (name: string) => void;
  onEditGenderChange: (gender: string) => void;
  onSaveEdit: () => void;
  onCancelEdit: () => void;
  isUpdating: boolean;
}> = (props) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: props.character.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.8 : 1,
  };

  return (
    <div ref={setNodeRef} style={style} className={`character-item ${isDragging ? 'dragging' : ''}`}>
      <div className="character-main" onClick={() => !props.isEditing && props.onCharacterClick(props.character)}>
        <div className="drag-handle" {...attributes} {...listeners} title="Перетащите для изменения порядка">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="16" height="16">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8h16M4 16h16" />
          </svg>
        </div>
        <div className="character-progress">
          <CharacterProgress characterId={props.character.id} />
        </div>
        <div className="character-name">
          {props.isEditing ? (
            <div className="character-edit-form">
              <TextInput
                type="text"
                value={props.editName}
                onChange={(e) => props.onEditNameChange(e.target.value)}
                placeholder="Имя персонажа"
              />
              <Select
                size="m"
                width="max"
                placeholder="Пол персонажа"
                value={[props.editGender]}
                onUpdate={(values) => props.onEditGenderChange(values[0] || 'unknown')}
              >
                <Select.Option value="unknown">Не указан</Select.Option>
                <Select.Option value="male">Мужской</Select.Option>
                <Select.Option value="female">Женский</Select.Option>
              </Select>
            </div>
          ) : (
            <>
              <Text variant="body-3">{props.character.name}</Text>
              {props.character.aliases && props.character.aliases.length > 0 && (
                <div className="character-aliases">
                  Алиасы: {props.character.aliases.join(", ")}
                </div>
              )}
            </>
          )}
        </div>
      </div>

      <div className="character-actions">
        {props.isEditing ? (
          <>
            <Button
              onClick={props.onSaveEdit}
              disabled={props.isUpdating || !props.editName.trim()}
              view="action"
              size="s"
            >
              {props.isUpdating ? "Сохранение..." : "Сохранить"}
            </Button>
            <Button
              onClick={props.onCancelEdit}
              view="outlined"
              size="s"
            >
              Отменить
            </Button>
          </>
        ) : (
          <>
            <Button
              onClick={(e) => {
                e.stopPropagation();
                props.onEditCharacter(props.character);
              }}
              view="outlined"
              size="s"
              title="Редактировать персонажа"
            >
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="16" height="16">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </Button>
            <Button
              onClick={(e) => {
                e.stopPropagation();
                props.onDeleteCharacter(props.character);
              }}
              view="outlined"
              size="s"
              title="Удалить персонаж"
            >
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </Button>
          </>
        )}
      </div>
    </div>
  );
};

// Компонент для отображения прогресса персонажа
const CharacterProgress: React.FC<{ characterId: number }> = ({ characterId }) => {
  const {
    data: progress,
    isLoading,
    error,
  } = useQuery<Array<{ completion_percentage?: number }>>(
    ["character-progress", characterId],
    () => checklistApi.getCharacterProgress(characterId) as Promise<Array<{ completion_percentage?: number }>>,
    {
      staleTime: 2 * 60 * 1000, // 2 минуты
      enabled: !!characterId,
    }
  );

  // Вычисляем общий процент заполненности
  const overallProgress =
    progress && progress.length > 0
      ? Math.round(
          progress.reduce(
            (sum: number, item) => sum + (item.completion_percentage || 0),
            0
          ) / progress.length
        )
      : 0;

  if (isLoading) {
    return <div className="character-progress-loading"></div>;
  }

  if (error) {
    return <div className="character-progress-error">Ошибка</div>;
  }

  return (
    <div className="character-progress-track">
      <Progress
        value={overallProgress}
        theme="success"
        text={`${overallProgress}%`}
      />
    </div>
  );
};

// Компонент для отображения секции текста с персонажами
const TextSection: React.FC<{
  text: ProjectText;
  onCharacterClick: (character: Character) => void;
  onEditCharacter: (character: Character) => void;
  onDeleteCharacter: (character: Character) => void;
  editingCharacter: Character | null;
  editCharacterName: string;
  editCharacterGender: string;
  onEditNameChange: (name: string) => void;
  onEditGenderChange: (gender: string) => void;
  onSaveEdit: () => void;
  onCancelEdit: () => void;
  isUpdating: boolean;
  onDragEnd: (event: DragEndEvent) => void;
  sensors: ReturnType<typeof useSensors>;
}> = ({
  text,
  onCharacterClick,
  onEditCharacter,
  onDeleteCharacter,
  editingCharacter,
  editCharacterName,
  editCharacterGender,
  onEditNameChange,
  onEditGenderChange,
  onSaveEdit,
  onCancelEdit,
  isUpdating,
  onDragEnd,
  sensors
}) => {
  const {
    data: characters,
    isLoading: charactersLoading,
    error: charactersError,
  } = useQuery<Character[]>(
    ["text-characters", text.id],
    () => fetchCharacters(text.id.toString()),
    {
      enabled: !!text.processed_at, // Загружаем персонажей только если текст обработан
      staleTime: 5 * 60 * 1000, // 5 минут
    }
  );

  return (
    <div className="text-section">
      <div className="text-header">
        <h3>{text.filename}</h3>
        <span
          className={`status-badge ${
            text.processed_at ? "processed" : "pending"
          }`}
        >
          {text.processed_at ? "Обработан" : "В ожидании"}
        </span>
      </div>

      <div className="file-status-info">
        {text.processed_at ? (
          <div className="processed-info">
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <span>Файл успешно обработан</span>
            <small>{new Date(text.processed_at).toLocaleString("ru-RU")}</small>
          </div>
        ) : (
          <div className="pending-info">
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <span>Ожидает обработки</span>
          </div>
        )}
      </div>

      {/* Отображение персонажей только для обработанных текстов */}
      {text.processed_at && (
        <>
          {charactersLoading && (
            <div className="characters-loading">
              <div className="spinner"></div>
              <span>Загрузка персонажей...</span>
            </div>
          )}

          {charactersError && (
            <div className="error-state">
              <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"
                />
              </svg>
              <p>Ошибка загрузки персонажей</p>
            </div>
          )}

          {characters && characters.length > 0 && (
            <DndContext
              sensors={sensors}
              collisionDetection={closestCenter}
              onDragEnd={onDragEnd}
            >
              <SortableContext
                items={characters.map(c => c.id)}
                strategy={verticalListSortingStrategy}
              >
                <div className="characters-grid">
                  {characters.map((character) => (
                    <SortableCharacterItem
                      key={character.id}
                      character={character}
                      onCharacterClick={onCharacterClick}
                      onEditCharacter={onEditCharacter}
                      onDeleteCharacter={onDeleteCharacter}
                      isEditing={editingCharacter?.id === character.id}
                      editName={editCharacterName}
                      editGender={editCharacterGender}
                      onEditNameChange={onEditNameChange}
                      onEditGenderChange={onEditGenderChange}
                      onSaveEdit={onSaveEdit}
                      onCancelEdit={onCancelEdit}
                      isUpdating={isUpdating}
                    />
                  ))}
                </div>
              </SortableContext>
            </DndContext>
          )}

          {characters && characters.length === 0 && (
            <div className="empty-characters">
              <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
                />
              </svg>
              <p>Персонажи не найдены</p>
            </div>
          )}
        </>
      )}
    </div>
  );
};

const ProjectDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [showAddCharacterForm, setShowAddCharacterForm] = useState<boolean>(false);
  const [newCharacterName, setNewCharacterName] = useState<string>("");
  const [newCharacterGender, setNewCharacterGender] = useState<"male" | "female" | "unknown">("unknown");
  const [editingCharacter, setEditingCharacter] = useState<Character | null>(null);
  const [editCharacterName, setEditCharacterName] = useState<string>("");
  const [editCharacterGender, setEditCharacterGender] = useState<"male" | "female" | "unknown">("unknown");

  const queryClient = useQueryClient();

  // Настройка сенсоров для @dnd-kit
  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  const deleteMutation = useMutation(deleteProject, {
    onSuccess: () => {
      // Перенаправляем пользователя на список проектов после удаления
      queryClient.invalidateQueries("projects");
      navigate("/");
    },
    onError: (error) => {
      console.error("Ошибка удаления проекта:", error);
      alert("Не удалось удалить проект. Попробуйте еще раз.");
    },
  });

  const {
    data: project,
    isLoading,
    error,
  } = useQuery<Project>(["project", id], () => fetchProject(id!), { enabled: !!id });

  const { data: texts } = useQuery<ProjectText[]>(
    ["project-texts", id],
    () => fetchProjectTexts(id!),
    { enabled: !!id }
  );

  const uploadMutation = useMutation((file: File) => uploadText(id!, file), {
    onSuccess: () => {
      queryClient.invalidateQueries(["project", id]);
      queryClient.invalidateQueries(["project-texts", id]);
      setSelectedFile(null);
    },
    onError: (error) => {
      console.error("Ошибка загрузки файла:", error);
    },
  });

  const createCharacterMutation = useMutation(
    ({ textId, characterData }: { textId: string; characterData: { name: string; gender?: "male" | "female" } }) =>
      charactersApi.create(textId, characterData),
    {
      onSuccess: () => {
        // Обновляем кэш персонажей для всех текстов
        texts?.forEach((text) => {
          queryClient.invalidateQueries(["text-characters", text.id]);
        });
        // Сбрасываем форму
        setNewCharacterName("");
        setNewCharacterGender("unknown");
        setShowAddCharacterForm(false);
      },
      onError: (error) => {
        console.error("Ошибка создания персонажа:", error);
        alert("Не удалось создать персонажа. Попробуйте еще раз.");
      },
    }
  );

  const deleteCharacterMutation = useMutation(
    (characterId: string) => charactersApi.delete(characterId),
    {
      onSuccess: () => {
        // Обновляем кэш персонажей для всех текстов
        texts?.forEach((text) => {
          queryClient.invalidateQueries(["text-characters", text.id]);
        });
      },
      onError: (error) => {
        console.error("Ошибка удаления персонажа:", error);
        alert("Не удалось удалить персонажа. Попробуйте еще раз.");
      },
    }
  );

  const updateCharacterMutation = useMutation(
    ({ characterId, characterData }: { characterId: string; characterData: { name: string; gender?: "male" | "female" } }) =>
      charactersApi.update(characterId, characterData),
    {
      onSuccess: () => {
        // Обновляем кэш персонажей для всех текстов
        texts?.forEach((text) => {
          queryClient.invalidateQueries(["text-characters", text.id]);
        });
        // Сбрасываем форму редактирования
        setEditingCharacter(null);
        setEditCharacterName("");
        setEditCharacterGender("unknown");
      },
      onError: (error) => {
        console.error("Ошибка обновления персонажа:", error);
        alert("Не удалось обновить персонажа. Попробуйте еще раз.");
      },
    }
  );

  const updateCharactersOrderMutation = useMutation(
    (charactersData: Array<{id: number, sort_order: number}>) =>
      charactersApi.updateOrder(charactersData),
    {
      onSuccess: () => {
        // Обновляем кэш персонажей для всех текстов
        texts?.forEach((text) => {
          queryClient.invalidateQueries(["text-characters", text.id]);
        });
      },
      onError: (error) => {
        console.error("Ошибка обновления порядка персонажей:", error);
        alert("Не удалось обновить порядок персонажей. Попробуйте еще раз.");
      },
    }
  );

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (
      file &&
      (file.type === "text/plain" ||
        file.name.toLowerCase().endsWith(".fb2") ||
        file.name.toLowerCase().endsWith(".epub"))
    ) {
      setSelectedFile(file);
    } else {
      alert("Пожалуйста, выберите файл в формате TXT или FB2");
    }
  };

  const handleUpload = () => {
    if (selectedFile) {
      uploadMutation.mutate(selectedFile);
    }
  };

  const handleCharacterClick = (character: Character) => {
    navigate(`/characters/${character.id}/checklists`);
  };

  const handleDeleteProject = () => {
    if (!project) return;

    if (
      window.confirm(
        `Вы уверены, что хотите удалить проект "${project.title}"? Это действие нельзя отменить и все данные проекта будут удалены.`
      )
    ) {
      deleteMutation.mutate(id!);
    }
  };

  const handleAddCharacter = () => {
    if (!newCharacterName.trim()) {
      alert("Пожалуйста, введите имя персонажа");
      return;
    }

    // Находим первый обработанный текст для добавления персонажа
    const processedText = texts?.find((text) => text.processed_at);
    if (!processedText) {
      alert("Для добавления персонажа необходимо загрузить и обработать хотя бы один текст");
      return;
    }

    const characterData = {
      name: newCharacterName.trim(),
      gender: newCharacterGender !== "unknown" ? newCharacterGender : undefined,
    };

    createCharacterMutation.mutate({
      textId: processedText.id.toString(),
      characterData,
    });
  };

  const handleCancelAddCharacter = () => {
    setNewCharacterName("");
    setNewCharacterGender("unknown");
    setShowAddCharacterForm(false);
  };

  const handleEditCharacter = (character: Character) => {
    setEditingCharacter(character);
    setEditCharacterName(character.name);
    setEditCharacterGender(character.gender || "unknown");
  };

  const handleUpdateCharacter = () => {
    if (!editingCharacter || !editCharacterName.trim()) {
      alert("Пожалуйста, введите имя персонажа");
      return;
    }

    const characterData = {
      name: editCharacterName.trim(),
      gender: editCharacterGender !== "unknown" ? editCharacterGender : undefined,
    };

    updateCharacterMutation.mutate({
      characterId: editingCharacter.id.toString(),
      characterData,
    });
  };

  const handleCancelEditCharacter = () => {
    setEditingCharacter(null);
    setEditCharacterName("");
    setEditCharacterGender("unknown");
  };

  const handleDeleteCharacter = (character: Character) => {
    if (window.confirm(`Вы уверены, что хотите удалить персонажа "${character.name}"? Это действие нельзя отменить и все данные анализа персонажа будут удалены.`)) {
      deleteCharacterMutation.mutate(character.id.toString());
    }
  };

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;

    if (!over || active.id === over.id) return;

    // Находим текст, содержащий перетаскиваемый персонаж
    let targetTextId: number | null = null;
    let characters: Character[] | null = null;

    for (const text of texts || []) {
      const charactersQueryKey = ["text-characters", text.id];
      const textCharacters = queryClient.getQueryData<Character[]>(charactersQueryKey);
      if (textCharacters?.some(char => char.id === active.id)) {
        targetTextId = text.id;
        characters = textCharacters;
        break;
      }
    }

    if (!targetTextId || !characters) return;

    const oldIndex = characters.findIndex(char => char.id === active.id);
    const newIndex = characters.findIndex(char => char.id === over.id);

    if (oldIndex === -1 || newIndex === -1) return;

    // Создаем новый массив с обновленным порядком
    const reorderedCharacters = arrayMove(characters, oldIndex, newIndex);

    // Обновляем sort_order для всех персонажей
    const updatedCharacters = reorderedCharacters.map((char, index) => ({
      id: char.id,
      sort_order: index
    }));

    // Оптимистично обновляем кэш
    const charactersQueryKey = ["text-characters", targetTextId];
    queryClient.setQueryData(charactersQueryKey, reorderedCharacters.map((char, index) => ({
      ...char,
      sort_order: index
    })));

    // Отправляем обновления на сервер
    updateCharactersOrderMutation.mutate(updatedCharacters);
  };

  if (isLoading) {
    return (
      <div className="container">
        <div className="loading">
          <div className="spinner"></div>
        </div>
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="container">
        <div className="empty-state">
          <div className="empty-icon">
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"
              />
            </svg>
          </div>
          <h3 className="empty-title">Проект не найден</h3>
          <p className="empty-description">
            Проект с указанным ID не существует
          </p>
          <Button href="/">
            Вернуться к проектам
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="project-detail-header">
        <div className="project-detail-header-top">
          <div>
            <Text variant="display-1">{project.title}</Text>
            {project.description && <p>{project.description}</p>}
          </div>
          <Button
            onClick={handleDeleteProject}
            disabled={deleteMutation.isLoading}
            size="l"
          >
            {deleteMutation.isLoading ? (
              <div className="project-detail-delete">
                <span className="spinner small"></span>
                <span>Удаление...</span>
              </div>
            ) : (
              "Удалить проект"
            )}
          </Button>
        </div>
        <div className="project-meta">
          <span>
            Создан: {new Date(project.created_at).toLocaleDateString("ru-RU")}
          </span>
          <span>•</span>
          <span>
            Обновлен: {new Date(project.updated_at).toLocaleDateString("ru-RU")}
          </span>
        </div>
      </div>

      <div className="project-content">
        <div className="main-section">
          <div className="card">
            <div className="card-header">
              <h2 className="card-title">Загрузка текста</h2>
            </div>

            <div className="file-upload">
              <div className="upload-area">
                <div className="upload-content">
                  <label htmlFor="file-upload" className="upload-label">
                    <div className="upload-icon">
                      <svg
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                        />
                      </svg>
                    </div>
                    {selectedFile
                      ? selectedFile.name
                      : "Перетащите файл сюда или нажмите для выбора"}
                    <p className="upload-help">
                      Поддерживаются файлы TXT, FB2 и EPUB до 10MB
                    </p>
                  </label>
                  <input
                    id="file-upload"
                    type="file"
                    accept=".txt,.fb2,.epub"
                    onChange={handleFileSelect}
                    style={{ display: "none" }}
                  />
                </div>
              </div>

              <Button
                disabled={!selectedFile || uploadMutation.isLoading}
                onClick={handleUpload}
                view="action"
                size="l"
              >
                {uploadMutation.isLoading ? (
                  <div className="project-detail-button">
                    <span className="spinner small"></span>
                    Обработка файла...
                  </div>
                ) : (
                  "Загрузить и обработать текст"
                )}
              </Button>

              {uploadMutation.isError && (
                <div className="error-message">
                  <strong>Ошибка загрузки файла</strong>
                  <p>
                    Не удалось загрузить и обработать файл. Попробуйте еще раз.
                  </p>
                </div>
              )}

              {uploadMutation.isSuccess && uploadMutation.data && (
                <div className="success-message">
                  <strong>Файл успешно загружен</strong>
                  <div className="upload-stats">
                    <p>Имя файла: {uploadMutation.data.filename}</p>
                    <p>Формат: {uploadMutation.data.format?.toUpperCase()}</p>
                    <p>
                      Размер содержимого:{" "}
                      {uploadMutation.data.content_length?.toLocaleString() ||
                        "N/A"}{" "}
                      символов
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Секция найденных персонажей */}
          {texts && texts.length > 0 && (
            <div className="card">
              <div className="card-header">
                <h2 className="card-title">Найденные персонажи</h2>
                {texts.some((text) => text.processed_at) && (
                  <Button
                    onClick={() => setShowAddCharacterForm(!showAddCharacterForm)}
                    view="outlined"
                    size="m"
                  >
                    {showAddCharacterForm ? "Отменить" : "Добавить персонажа"}
                  </Button>
                )}
              </div>

              {/* Форма добавления персонажа */}
              {showAddCharacterForm && (
                <div className="add-character-form">
                  <div className="form-group">
                    <label htmlFor="character-name">Имя персонажа:</label>
                    <TextInput
                      id="character-name"
                      value={newCharacterName}
                      onChange={(e) => setNewCharacterName(e.target.value)}
                      placeholder="Введите имя персонажа"
                    />
                  </div>

                  <div className="form-group">
                    <label htmlFor="character-gender">Пол персонажа:</label>
                    <Select
                      id="character-gender"
                      size="m"
                      width="max"
                      placeholder="Пол персонажа"
                      value={[newCharacterGender]}
                      onUpdate={(values) => setNewCharacterGender((values[0] || 'unknown')  as "male" | "female" | "unknown")}
                    >
                      <Select.Option value="unknown">Не указан</Select.Option>
                      <Select.Option value="male">Мужской</Select.Option>
                      <Select.Option value="female">Женский</Select.Option>
                    </Select>
                  </div>

                  <div className="form-actions">
                    <Button
                      onClick={handleAddCharacter}
                      disabled={createCharacterMutation.isLoading || !newCharacterName.trim()}
                      view="action"
                      size="m"
                    >
                      {createCharacterMutation.isLoading ? "Создание..." : "Создать персонажа"}
                    </Button>
                    <Button
                      onClick={handleCancelAddCharacter}
                      view="outlined"
                      size="m"
                    >
                      Отменить
                    </Button>
                  </div>

                  {createCharacterMutation.isError && (
                    <div className="error-message">
                      <strong>Ошибка создания персонажа</strong>
                      <p>Не удалось создать персонажа. Попробуйте еще раз.</p>
                    </div>
                  )}
                </div>
              )}

              {texts.map((text) => (
                <TextSection
                  key={text.id}
                  text={text}
                  onCharacterClick={handleCharacterClick}
                  onEditCharacter={handleEditCharacter}
                  onDeleteCharacter={handleDeleteCharacter}
                  editingCharacter={editingCharacter}
                  editCharacterName={editCharacterName}
                  editCharacterGender={editCharacterGender}
                  onEditNameChange={setEditCharacterName}
                  onEditGenderChange={(gender) => setEditCharacterGender(gender as "male" | "female" | "unknown")}
                  onSaveEdit={handleUpdateCharacter}
                  onCancelEdit={handleCancelEditCharacter}
                  isUpdating={updateCharacterMutation.isLoading}
                  onDragEnd={handleDragEnd}
                  sensors={sensors}
                />
              ))}
            </div>
          )}
        </div>

        <div className="sidebar">
          <div className="card">
            <h3>Статистика проекта</h3>

            <div className="stats-list">
              <div className="stat-item">
                <span>Загружено текстов:</span>
                <strong>{texts?.length || 0}</strong>
              </div>
              <div className="stat-item">
                <span>Обработано:</span>
                <strong>
                  {texts?.filter((text) => text.processed_at).length || 0}
                </strong>
              </div>
              <div className="stat-item">
                <span>Форматы:</span>
                <strong>
                  {texts
                    ? [...new Set(texts.map((t) => t.original_format))]
                        .join(", ")
                        .toUpperCase()
                    : "Нет"}
                </strong>
              </div>
            </div>

            {/* Список файлов */}
            {texts && texts.length > 0 && (
              <div className="files-list">
                <h4>Загруженные файлы:</h4>
                {texts.map((text) => (
                  <div key={text.id} className="file-item">
                    <div className="file-info">
                      <div className="filename">{text.filename}</div>
                      <div className="file-details">
                        <span className="format">
                          {text.original_format.toUpperCase()}
                        </span>
                        <span
                          className={`status ${
                            text.processed_at ? "processed" : "pending"
                          }`}
                        >
                          {text.processed_at ? "✓ Обработан" : "⏳ В ожидании"}
                        </span>
                      </div>
                      {text.processed_at && (
                        <div className="processed-date">
                          {new Date(text.processed_at).toLocaleDateString(
                            "ru-RU"
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProjectDetail;
