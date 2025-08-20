import React, { useEffect } from 'react';
import { createPortal } from 'react-dom';
import { Button } from "@gravity-ui/uikit";

interface DownloadModalProps {
  isOpen: boolean;
  fileName: string;
  dataUrl: string;
  onClose: () => void;
}

export const DownloadModal: React.FC<DownloadModalProps> = ({
  isOpen,
  fileName,
  dataUrl,
  onClose
}) => {
  // Обработка клавиши ESC для закрытия модального окна
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown);
      // Блокируем скролл страницы при открытом модальном окне
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  // Автоматическое закрытие через 30 секунд
  useEffect(() => {
    if (isOpen) {
      const timer = setTimeout(() => {
        onClose();
      }, 30000);

      return () => clearTimeout(timer);
    }
  }, [isOpen, onClose]);

  const handleOverlayClick = (e: React.MouseEvent) => {
    // Закрываем модальное окно только при клике на overlay
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  if (!isOpen) return null;

  const modalContent = (
    <div className="download-modal-overlay" onClick={handleOverlayClick}>
      <div className="download-modal">
        <div className="download-modal__content">
          <div className="download-modal__instruction">
            <h3>Скачивание файла</h3>
            <p>
              Нажмите на кнопку ниже, затем в открывшемся окне используйте кнопку "Поделиться" и выберите "Сохранить в Файлы"
            </p>
          </div>

          <Button
            href={dataUrl}
            view="action"
            download={fileName}
            target="_blank"
            rel="noopener noreferrer"
          >
            Скачать {fileName}
          </Button>

          <Button
            className="download-modal__close"
            onClick={onClose}
            type="button"
          >
            ✕
          </Button>
        </div>
      </div>
    </div>
  );

  // Используем портал для рендера модального окна в body
  return createPortal(modalContent, document.body);
};
