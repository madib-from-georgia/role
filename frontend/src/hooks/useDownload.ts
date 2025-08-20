import { useContext } from 'react';
import { DownloadContext, DownloadContextType } from '../contexts/downloadContextDefinition';

/**
 * Хук для использования контекста скачивания файлов
 */
export const useDownload = (): DownloadContextType => {
  const context = useContext(DownloadContext);
  
  if (context === undefined) {
    throw new Error('useDownload must be used within a DownloadProvider');
  }
  
  return context;
};
