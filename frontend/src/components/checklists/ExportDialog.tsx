import React, { useState } from 'react';
import { useMutation, useQuery } from 'react-query';
import { exportApi } from '../../services/api';
import { downloadFile, extractFileName, formatFileSize } from '../../utils/downloadFile';

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

  // Загружаем доступные форматы и типы
  const { data: formats } = useQuery('export-formats', exportApi.getFormats);
  const { data: types } = useQuery('export-types', exportApi.getTypes);

  // Мутация для экспорта
  const exportMutation = useMutation(exportApi.exportCharacter, {
    onSuccess: (response) => {
      // Используем утилиту для скачивания
      downloadFile(response.data, response.fileName);
      
      // Показываем успешное сообщение
      const fileSize = formatFileSize(response.data.size);
      alert(`Файл "${response.fileName}" (${fileSize}) успешно скачан!`);
      
      // Закрываем диалог
      onClose();
    },
    onError: (error: any) => {
      console.error('Ошибка экспорта:', error);
      
      // Более детальное сообщение об ошибке
      let errorMessage = 'Ошибка при экспорте файла.';
      if (error.response?.status === 403) {
        errorMessage = 'Нет доступа к данному персонажу.';
      } else if (error.response?.status === 404) {
        errorMessage = 'Персонаж не найден.';
      } else if (error.response?.status >= 500) {
        errorMessage = 'Внутренняя ошибка сервера. Попробуйте позже.';
      }
      
      alert(errorMessage + ' Попробуйте еще раз.');
    }
  });

  const handleExport = () => {
    exportMutation.mutate({
      character_id: characterId,
      format,
      export_type: exportType,
      include_empty_responses: includeEmptyResponses
    });
  };

  if (!isOpen) return null;

  return (
    <div className="export-dialog-overlay">
      <div className="export-dialog">
        <div className="export-dialog__header">
          <h2>Экспорт анализа персонажа</h2>
          <button 
            className="export-dialog__close"
            onClick={onClose}
            disabled={exportMutation.isLoading}
          >
            ×
          </button>
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
                  <input
                    type="radio"
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
                  <input
                    type="radio"
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
                  <input
                    type="radio"
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
                  <input
                    type="radio"
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
                  <input
                    type="radio"
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
                <input
                  type="checkbox"
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
          <button
            className="btn btn-secondary"
            onClick={onClose}
            disabled={exportMutation.isLoading}
          >
            Отмена
          </button>
          <button
            className="btn btn-primary"
            onClick={handleExport}
            disabled={exportMutation.isLoading}
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
          </button>
        </div>
      </div>
    </div>
  );
};
