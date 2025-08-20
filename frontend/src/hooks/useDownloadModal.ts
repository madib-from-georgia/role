import { useState, useCallback } from 'react';

interface DownloadModalState {
  isOpen: boolean;
  fileName: string;
  dataUrl: string;
}

interface UseDownloadModalReturn {
  modalState: DownloadModalState;
  showModal: (fileName: string, dataUrl: string) => void;
  hideModal: () => void;
}

/**
 * Хук для управления состоянием модального окна скачивания файлов
 */
export const useDownloadModal = (): UseDownloadModalReturn => {
  const [modalState, setModalState] = useState<DownloadModalState>({
    isOpen: false,
    fileName: '',
    dataUrl: ''
  });

  const showModal = useCallback((fileName: string, dataUrl: string) => {
    setModalState({
      isOpen: true,
      fileName,
      dataUrl
    });
  }, []);

  const hideModal = useCallback(() => {
    setModalState(prev => ({
      ...prev,
      isOpen: false
    }));
    
    // Очищаем данные через небольшую задержку после закрытия анимации
    setTimeout(() => {
      setModalState({
        isOpen: false,
        fileName: '',
        dataUrl: ''
      });
    }, 300);
  }, []);

  return {
    modalState,
    showModal,
    hideModal
  };
};
