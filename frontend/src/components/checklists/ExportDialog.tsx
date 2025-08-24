import React, { useState, useEffect } from 'react';
import { useMutation } from 'react-query';
import { Button, Radio, Checkbox, Icon } from "@gravity-ui/uikit";
import { Xmark } from "@gravity-ui/icons";
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
  const [reportType, setReportType] = useState<'questionnaire_empty' | 'questionnaire_with_answers' | 'questionnaire_full' | 'answers_only'>('questionnaire_with_answers');
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
        // Убираем фокус с активного элемента перед закрытием
        if (document.activeElement instanceof HTMLElement) {
          document.activeElement.blur();
        }
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
      report_type: reportType,
      include_empty_responses: includeEmptyResponses
    });
  };

  const handleOverlayClick = (e: React.MouseEvent) => {
    // Закрываем диалог только если кликнули по overlay, а не по самому диалогу
    if (e.target === e.currentTarget && !exportMutation.isLoading) {
      // Убираем фокус с активного элемента перед закрытием
      if (document.activeElement instanceof HTMLElement) {
        document.activeElement.blur();
      }
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
            <Icon data={Xmark} />
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

            {/* Выбор типа отчета */}
            <div className="export-option-group">
              <label className="export-label">Типы отчетов:</label>
              <div className="export-radio-group">
                <label className="export-radio">
                  <Radio
                    value="questionnaire_empty"
                    checked={reportType === 'questionnaire_empty'}
                    onChange={(e) => setReportType(e.target.value as 'questionnaire_empty')}
                    disabled={exportMutation.isLoading}
                  />
                  <span className="export-radio-label">
                    <strong>Опросник без ответов</strong>
                    <small>Только вопросы и варианты ответов. Без ответов пользователя</small>
                  </span>
                </label>
                <label className="export-radio">
                  <Radio
                    value="questionnaire_with_answers"
                    checked={reportType === 'questionnaire_with_answers'}
                    onChange={(e) => setReportType(e.target.value as 'questionnaire_with_answers')}
                    disabled={exportMutation.isLoading}
                  />
                  <span className="export-radio-label">
                    <strong>Опросник с ответами</strong>
                    <small>Вопрос и ответ пользователя</small>
                  </span>
                </label>
                <label className="export-radio">
                  <Radio
                    value="questionnaire_full"
                    checked={reportType === 'questionnaire_full'}
                    onChange={(e) => setReportType(e.target.value as 'questionnaire_full')}
                    disabled={exportMutation.isLoading}
                  />
                  <span className="export-radio-label">
                    <strong>Опросник с ответами, советами и упражнениями</strong>
                    <small>Вопрос и ответ пользователя с советами к каждому ответу и упражнениями</small>
                  </span>
                </label>
                <label className="export-radio">
                  <Radio
                    value="answers_only"
                    checked={reportType === 'answers_only'}
                    onChange={(e) => setReportType(e.target.value as 'answers_only')}
                    disabled={exportMutation.isLoading}
                  />
                  <span className="export-radio-label">
                    <strong>Список ответов пользователя</strong>
                    <small>Только ответ на каждый вопрос, чтобы возник текст, характеризующий персонажа</small>
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
