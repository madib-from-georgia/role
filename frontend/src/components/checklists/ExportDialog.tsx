import React, { useState, useEffect } from 'react';
import { useMutation } from 'react-query';
import { Button, Radio, Checkbox } from "@gravity-ui/uikit";
import { exportApi } from '../../services/api';
import { downloadFile, formatFileSize, isMobileDevice, isIOSSafari } from '../../utils/downloadFile';
import { ApiError } from '../../types/common';

interface ExportDialogProps {
  characterId: number;
  characterName: string;
  onClose: () => void;
  isOpen: boolean;
}

export const ExportDialog: React.FC<ExportDialogProps> = ({
  characterId,
  characterName,
  onClose,
  isOpen
}) => {
  const [format, setFormat] = useState<'pdf' | 'docx'>('pdf');
  const [exportType, setExportType] = useState<'detailed' | 'summary' | 'compact'>('detailed');
  const [includeEmptyResponses, setIncludeEmptyResponses] = useState(false);

  // Загружаем доступные форматы и типы (закомментировано, так как не используется)
  // const { data: formats } = useQuery('export-formats', exportApi.getFormats);
  // const { data: types } = useQuery('export-types', exportApi.getTypes);

  // Мутация для экспорта
  const exportMutation = useMutation(exportApi.exportCharacter, {
    onSuccess: async (response) => {
      try {
        // Используем утилиту для скачивания
        await downloadFile(response.data, response.fileName);

        // Показываем успешное сообщение с учетом типа устройства
        const fileSize = formatFileSize(response.data.size);

        if (isMobileDevice()) {
          if (isIOSSafari()) {
            // Для iOS Safari не показываем alert, так как появится модальное окно с инструкциями
            console.log(`Файл "${response.fileName}" (${fileSize}) готов к скачиванию в iOS Safari`);
          } else {
            alert(`Файл "${response.fileName}" (${fileSize}) готов к скачиванию. Если файл открылся в браузере, используйте меню браузера для сохранения файла.`);
          }
        } else {
          alert(`Файл "${response.fileName}" (${fileSize}) успешно скачан!`);
        }

        // Закрываем диалог
        onClose();
      } catch (error) {
        console.error('Ошибка при скачивании файла:', error);
        alert('Произошла ошибка при скачивании файла. Попробуйте еще раз.');
      }
    },
    onError: (error: ApiError) => {
      console.error('Ошибка экспорта:', error);

      // Более детальное сообщение об ошибке
      let errorMessage = 'Ошибка при экспорте файла.';
      if (error.response?.status === 403) {
        errorMessage = 'Нет доступа к данному персонажу.';
      } else if (error.response?.status === 404) {
        errorMessage = 'Персонаж не найден.';
      } else if (error.response?.status && error.response.status >= 500) {
        errorMessage = 'Внутренняя ошибка сервера. Попробуйте позже.';
      }

      alert(errorMessage + ' Попробуйте еще раз.');
    }
  });

  // Обработка клавиши ESC для закрытия диалога
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && isOpen && !exportMutation.isLoading) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown);
    }

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen, onClose, exportMutation.isLoading]);

  const handleExport = () => {
    exportMutation.mutate({
      character_id: characterId,
      format,
      export_type: exportType,
      include_empty_responses: includeEmptyResponses
    });
  };

  const handleOverlayClick = (e: React.MouseEvent) => {
    // Закрываем диалог только если кликнули по overlay, а не по самому диалогу
    if (e.target === e.currentTarget && !exportMutation.isLoading) {
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="export-dialog-overlay" onClick={handleOverlayClick}>
      <div className="export-dialog">
        <div className="export-dialog__header">
          <h2>Экспорт анализа персонажа</h2>
          <Button
            onClick={onClose}
            disabled={exportMutation.isLoading}
          >
            ×
          </Button>
        </div>

        <div className="export-dialog__content">
          <div className="export-character-info">
            <h3>Персонаж: <span className="character-name">{characterName}</span></h3>
            <p className="export-description">
              Создайте отчет по анализу персонажа в удобном формате для просмотра, печати или редактирования.
            </p>
          </div>

          <div className="export-options">
            {/* Выбор формата */}
            <div className="export-option-group">
              <label className="export-label">Формат файла:</label>
              <div className="export-radio-group">
                <label className="export-radio">
                  <Radio
                    value="pdf"
                    checked={format === 'pdf'}
                    onChange={(e) => setFormat(e.target.value as 'pdf')}
                    disabled={exportMutation.isLoading}
                  />
                  <span className="export-radio-label">
                    <strong>PDF</strong>
                    <small>Универсальный формат для просмотра и печати</small>
                  </span>
                </label>
                <label className="export-radio">
                  <Radio
                    value="docx"
                    checked={format === 'docx'}
                    onChange={(e) => setFormat(e.target.value as 'docx')}
                    disabled={exportMutation.isLoading}
                  />
                  <span className="export-radio-label">
                    <strong>DOCX</strong>
                    <small>Документ Word для редактирования</small>
                  </span>
                </label>
              </div>
            </div>

            {/* Выбор типа детализации */}
            <div className="export-option-group">
              <label className="export-label">Детализация:</label>
              <div className="export-radio-group">
                <label className="export-radio">
                  <Radio
                    value="detailed"
                    checked={exportType === 'detailed'}
                    onChange={(e) => setExportType(e.target.value as 'detailed')}
                    disabled={exportMutation.isLoading}
                  />
                  <span className="export-radio-label">
                    <strong>Подробный</strong>
                    <small>Все вопросы и ответы с комментариями</small>
                  </span>
                </label>
                <label className="export-radio">
                  <Radio
                    value="summary"
                    checked={exportType === 'summary'}
                    onChange={(e) => setExportType(e.target.value as 'summary')}
                    disabled={exportMutation.isLoading}
                  />
                  <span className="export-radio-label">
                    <strong>Краткий</strong>
                    <small>Сводка по чеклистам со статистикой</small>
                  </span>
                </label>
                <label className="export-radio">
                  <Radio
                    value="compact"
                    checked={exportType === 'compact'}
                    onChange={(e) => setExportType(e.target.value as 'compact')}
                    disabled={exportMutation.isLoading}
                  />
                  <span className="export-radio-label">
                    <strong>Компактный</strong>
                    <small>Только основная статистика</small>
                  </span>
                </label>
              </div>
            </div>

            {/* Дополнительные опции */}
            <div className="export-option-group">
              <label className="export-checkbox">
                <Checkbox
                  checked={includeEmptyResponses}
                  onChange={(e) => setIncludeEmptyResponses(e.target.checked)}
                  disabled={exportMutation.isLoading}
                />
                <span className="export-checkbox-label">
                  Включать вопросы без ответов
                </span>
              </label>
            </div>
          </div>
        </div>

        <div className="export-dialog__footer">
          <Button
            onClick={onClose}
            disabled={exportMutation.isLoading}
            size="l"
          >
            Отмена
          </Button>
          <Button
            onClick={handleExport}
            disabled={exportMutation.isLoading}
            view="action"
            size="l"
          >
            {exportMutation.isLoading ? (
              <>
                <div className="spinner small"></div>
                Экспорт...
              </>
            ) : (
              <>
                📄 Экспортировать {format.toUpperCase()}
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  );
};
