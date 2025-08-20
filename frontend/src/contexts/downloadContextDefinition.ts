import { createContext } from 'react';

export interface DownloadContextType {
  showDownloadModal: (fileName: string, dataUrl: string) => void;
}

export const DownloadContext = createContext<DownloadContextType | undefined>(undefined);
