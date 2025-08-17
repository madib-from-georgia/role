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
 * Конвертирует blob в data URL
 */
const blobToDataURL = (blob: Blob): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result as string);
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
};

/**
 * Создает временную ссылку для скачивания в iOS Safari
 */
const createIOSDownloadLink = async (blob: Blob, fileName: string): Promise<void> => {
  try {
    // Конвертируем blob в data URL
    const dataURL = await blobToDataURL(blob);
    
    // Создаем ссылку с data URL
    const link = document.createElement('a');
    link.href = dataURL;
    link.download = fileName;
    
    // Добавляем атрибуты для лучшей совместимости
    link.setAttribute('target', '_blank');
    link.setAttribute('rel', 'noopener noreferrer');
    
    // Стилизуем ссылку
    link.style.cssText = `
      position: fixed;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      z-index: 10000;
      background: #007bff;
      color: white;
      padding: 15px 25px;
      border-radius: 8px;
      text-decoration: none;
      font-size: 16px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.3);
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    `;
    
    link.textContent = `📄 Скачать ${fileName}`;
    
    // Создаем overlay
    const overlay = document.createElement('div');
    overlay.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0, 0, 0, 0.8);
      z-index: 9999;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 20px;
      box-sizing: border-box;
    `;
    
    // Добавляем инструкцию
    const instruction = document.createElement('div');
    instruction.innerHTML = `
      <div style="
        background: white;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 20px;
        text-align: center;
        max-width: 300px;
        color: #333;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      ">
        <h3 style="margin: 0 0 15px 0; font-size: 18px;">Скачивание файла</h3>
        <p style="margin: 0 0 15px 0; font-size: 14px; line-height: 1.4;">
          Нажмите на кнопку ниже, затем в открывшемся окне используйте кнопку "Поделиться" и выберите "Сохранить в Файлы"
        </p>
      </div>
    `;
    
    // Кнопка закрытия
    const closeButton = document.createElement('button');
    closeButton.textContent = '✕ Закрыть';
    closeButton.style.cssText = `
      background: #6c757d;
      color: white;
      border: none;
      padding: 10px 20px;
      border-radius: 6px;
      cursor: pointer;
      font-size: 14px;
      margin-top: 15px;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    `;
    
    closeButton.onclick = () => {
      overlay.remove();
    };
    
    overlay.appendChild(instruction);
    overlay.appendChild(link);
    overlay.appendChild(closeButton);
    document.body.appendChild(overlay);
    
    // Автоматически закрываем через 30 секунд
    setTimeout(() => {
      if (document.body.contains(overlay)) {
        overlay.remove();
      }
    }, 30000);
    
  } catch (error) {
    console.error('Ошибка создания data URL:', error);
    // Fallback к стандартному методу
    const url = window.URL.createObjectURL(blob);
    window.open(url, '_blank');
    setTimeout(() => window.URL.revokeObjectURL(url), 2000);
  }
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

  // Для iOS Safari используем специальный подход с data URL
  if (isIOSSafari()) {
    await createIOSDownloadLink(blob, fileName);
    return;
  }
  
  // Для других мобильных браузеров пробуем стандартный подход
  const url = window.URL.createObjectURL(blob);
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
