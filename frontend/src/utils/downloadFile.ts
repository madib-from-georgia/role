/**
 * Утилита для скачивания файлов из Blob данных
 * Оптимизирована для работы на мобильных устройствах
 */

/**
 * Определяет, является ли устройство мобильным
 */
export const isMobileDevice = (): boolean => {
  return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
};

/**
 * Определяет, является ли браузер Safari на iOS
 */
export const isIOSSafari = (): boolean => {
  const ua = navigator.userAgent;
  return /iPad|iPhone|iPod/.test(ua) && /Safari/.test(ua) && !/CriOS|FxiOS|OPiOS|mercury/.test(ua);
};

/**
 * Определяет MIME-тип файла по расширению
 */
const getMimeType = (fileName: string): string => {
  const extension = fileName.split('.').pop()?.toLowerCase();
  
  const mimeTypes: Record<string, string> = {
    'pdf': 'application/pdf',
    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'doc': 'application/msword',
    'txt': 'text/plain',
    'html': 'text/html',
    'json': 'application/json',
    'xml': 'application/xml',
    'zip': 'application/zip',
    'png': 'image/png',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'gif': 'image/gif',
    'svg': 'image/svg+xml'
  };
  
  return mimeTypes[extension || ''] || 'application/octet-stream';
};

/**
 * Создает blob с правильным MIME-типом
 */
const createTypedBlob = (blob: Blob, fileName: string): Blob => {
  const mimeType = getMimeType(fileName);
  
  // Если blob уже имеет правильный MIME-тип, возвращаем как есть
  if (blob.type === mimeType) {
    return blob;
  }
  
  // Создаем новый blob с правильным MIME-типом
  return new Blob([blob], { type: mimeType });
};

/**
 * Проверяет поддержку Web Share API
 */
const isWebShareSupported = (): boolean => {
  return 'share' in navigator && 'canShare' in navigator;
};

/**
 * Скачивание файла через Web Share API (для поддерживающих устройств)
 */
const shareFile = async (blob: Blob, fileName: string): Promise<boolean> => {
  if (!isWebShareSupported()) {
    return false;
  }

  try {
    const file = new File([blob], fileName, { type: blob.type });
    
    if (navigator.canShare && navigator.canShare({ files: [file] })) {
      await navigator.share({
        files: [file],
        title: 'Экспорт анализа персонажа',
        text: `Файл: ${fileName}`
      });
      return true;
    }
  } catch (error) {
    console.log('Web Share API не удалось использовать:', error);
  }
  
  return false;
};

/**
 * Создает модальное окно с инструкциями для iOS Safari
 */
const createDownloadModal = (url: string, fileName: string): void => {
  // Создаем модальное окно
  const modal = document.createElement('div');
  modal.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.8);
    z-index: 10000;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
    box-sizing: border-box;
  `;

  const content = document.createElement('div');
  content.style.cssText = `
    background: white;
    border-radius: 12px;
    padding: 24px;
    max-width: 400px;
    width: 100%;
    text-align: center;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  `;

  const title = document.createElement('h3');
  title.textContent = 'Скачивание файла';
  title.style.cssText = `
    margin: 0 0 16px 0;
    color: #333;
    font-size: 18px;
  `;

  const instruction = document.createElement('p');
  instruction.innerHTML = `
    Для скачивания файла <strong>${fileName}</strong>:<br><br>
    1. Нажмите на ссылку ниже<br>
    2. Нажмите и удерживайте файл<br>
    3. Выберите "Скачать связанный файл" или "Сохранить в Файлы"
  `;
  instruction.style.cssText = `
    margin: 0 0 20px 0;
    color: #666;
    line-height: 1.5;
    font-size: 14px;
  `;

  const downloadLink = document.createElement('a');
  downloadLink.href = url;
  downloadLink.download = fileName;
  downloadLink.textContent = `📄 ${fileName}`;
  downloadLink.style.cssText = `
    display: inline-block;
    background: #007bff;
    color: white;
    padding: 12px 24px;
    border-radius: 8px;
    text-decoration: none;
    font-weight: 500;
    margin-bottom: 16px;
  `;

  const closeButton = document.createElement('button');
  closeButton.textContent = 'Закрыть';
  closeButton.style.cssText = `
    background: #6c757d;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 14px;
  `;

  closeButton.onclick = () => {
    modal.remove();
    window.URL.revokeObjectURL(url);
  };

  content.appendChild(title);
  content.appendChild(instruction);
  content.appendChild(downloadLink);
  content.appendChild(closeButton);
  modal.appendChild(content);
  document.body.appendChild(modal);

  // Автоматически закрываем через 30 секунд
  setTimeout(() => {
    if (document.body.contains(modal)) {
      modal.remove();
      window.URL.revokeObjectURL(url);
    }
  }, 30000);
};

/**
 * Скачивание файла для мобильных устройств через открытие в новом окне
 */
const downloadFileMobile = async (blob: Blob, fileName: string) => {
  // Сначала пробуем Web Share API
  const shared = await shareFile(blob, fileName);
  if (shared) {
    return;
  }

  const url = window.URL.createObjectURL(blob);
  
  // Для iOS Safari используем специальный подход
  if (isIOSSafari()) {
    // Пробуем открыть в новом окне
    const newWindow = window.open(url, '_blank');
    
    // Если окно не открылось (блокировщик попапов), показываем модальное окно
    if (!newWindow) {
      createDownloadModal(url, fileName);
      return;
    }
    
    // Очищаем URL через некоторое время
    setTimeout(() => {
      window.URL.revokeObjectURL(url);
    }, 2000);
    
    return;
  }
  
  // Для других мобильных браузеров пробуем стандартный подход
  const link = document.createElement('a');
  link.href = url;
  link.download = fileName;
  
  // Делаем ссылку невидимой, но добавляем в DOM
  link.style.display = 'none';
  document.body.appendChild(link);
  
  // Имитируем клик пользователя
  const clickEvent = new MouseEvent('click', {
    view: window,
    bubbles: true,
    cancelable: true
  });
  
  link.dispatchEvent(clickEvent);
  
  // Очищаем ресурсы
  setTimeout(() => {
    link.remove();
    window.URL.revokeObjectURL(url);
  }, 100);
};

/**
 * Скачивание файла для десктопных браузеров
 */
const downloadFileDesktop = (blob: Blob, fileName: string) => {
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
 * Основная функция скачивания файлов
 * Автоматически выбирает подходящий метод в зависимости от устройства
 */
export const downloadFile = async (blob: Blob, fileName: string) => {
  // Создаем blob с правильным MIME-типом
  const typedBlob = createTypedBlob(blob, fileName);
  
  // Проверяем поддержку скачивания
  if (!isDownloadSupported()) {
    // Если скачивание не поддерживается, открываем в новом окне
    const url = window.URL.createObjectURL(typedBlob);
    window.open(url, '_blank');
    setTimeout(() => window.URL.revokeObjectURL(url), 1000);
    return;
  }
  
  // Выбираем метод в зависимости от устройства
  if (isMobileDevice()) {
    await downloadFileMobile(typedBlob, fileName);
  } else {
    downloadFileDesktop(typedBlob, fileName);
  }
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
