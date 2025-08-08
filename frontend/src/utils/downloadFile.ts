/**
 * Утилита для скачивания файлов из Blob данных
 */

export const downloadFile = (blob: Blob, fileName: string) => {
  // Создаем URL для blob
  const url = window.URL.createObjectURL(blob);
  
  // Создаем временную ссылку для скачивания
  const link = document.createElement('a');
  link.href = url;
  link.download = fileName;
  
  // Добавляем ссылку в DOM и кликаем
  document.body.appendChild(link);
  link.click();
  
  // Очищаем ресурсы
  link.remove();
  window.URL.revokeObjectURL(url);
};

/**
 * Получает безопасное имя файла из заголовков response
 */
export const extractFileName = (
  contentDisposition: string | null,
  defaultName: string,
  format: string
): string => {
  if (contentDisposition) {
    const fileNameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
    if (fileNameMatch && fileNameMatch[1]) {
      return fileNameMatch[1].replace(/['"]/g, '');
    }
  }
  
  const timestamp = new Date().toISOString().slice(0, 16).replace(/[:-]/g, '');
  return `${defaultName}_${timestamp}.${format}`;
};

/**
 * Форматирует размер файла для отображения
 */
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

/**
 * Проверяет поддержку скачивания файлов браузером
 */
export const isDownloadSupported = (): boolean => {
  const link = document.createElement('a');
  return typeof link.download !== 'undefined';
};
