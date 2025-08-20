import React, { ReactNode, useEffect } from 'react';
import { DownloadModal } from '../components/common/DownloadModal';
import { useDownloadModal } from '../hooks/useDownloadModal';
import { setGlobalDownloadModal } from '../utils/downloadFile';
import { DownloadContext, DownloadContextType } from './downloadContextDefinition';
import '../styles_v2/components/DownloadModal.css';

interface DownloadProviderProps {
  children: ReactNode;
}

/**
 * Провайдер контекста для управления модальным окном скачивания файлов
 */
export const DownloadProvider: React.FC<DownloadProviderProps> = ({ children }) => {
  const { modalState, showModal, hideModal } = useDownloadModal();

  // Устанавливаем глобальную функцию для использования в утилитах
  useEffect(() => {
    setGlobalDownloadModal(showModal);
    
    // Очищаем при размонтировании
    return () => {
      setGlobalDownloadModal(() => {
        console.warn('DownloadProvider был размонтирован, модальное окно недоступно');
      });
    };
  }, [showModal]);

  const contextValue: DownloadContextType = {
    showDownloadModal: showModal
  };

  return (
    <DownloadContext.Provider value={contextValue}>
      {children}
      <DownloadModal
        isOpen={modalState.isOpen}
        fileName={modalState.fileName}
        dataUrl={modalState.dataUrl}
        onClose={hideModal}
      />
    </DownloadContext.Provider>
  );
};

