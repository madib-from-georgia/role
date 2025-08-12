import axios, { AxiosInstance, AxiosRequestConfig } from 'axios'

const API_BASE_URL = window.location.origin

// Создаем axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Добавляем interceptor для автоматического добавления токена авторизации
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Добавляем interceptor для обработки ошибок авторизации
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    // Если получили 401 и это не retry попытка
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken) {
        try {
          // Пытаемся обновить токен
          const response = await axios.post(`${API_BASE_URL}/api/auth/refresh`, {
            refresh_token: refreshToken
          })

          const { access_token, refresh_token: newRefreshToken } = response.data
          
          // Сохраняем новые токены
          localStorage.setItem('access_token', access_token)
          localStorage.setItem('refresh_token', newRefreshToken)

          // Повторяем оригинальный запрос с новым токеном
          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return apiClient(originalRequest)
        } catch (refreshError) {
          // Если refresh не удался, очищаем токены и перенаправляем на login
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          window.location.href = '/'
          return Promise.reject(refreshError)
        }
      } else {
        // Нет refresh токена - очищаем все и перенаправляем
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/'
      }
    }

    return Promise.reject(error)
  }
)

// Экспортируем настроенный axios instance
export default apiClient

// Утилиты для работы с API
export const api = {
  get: <T = any>(url: string, config?: AxiosRequestConfig) => 
    apiClient.get<T>(url, config).then(response => response.data),
  
  post: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) => 
    apiClient.post<T>(url, data, config).then(response => response.data),
  
  put: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) => 
    apiClient.put<T>(url, data, config).then(response => response.data),
  
  delete: <T = any>(url: string, config?: AxiosRequestConfig) => 
    apiClient.delete<T>(url, config).then(response => response.data),
  
  patch: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) => 
    apiClient.patch<T>(url, data, config).then(response => response.data),
}

// Специализированные API методы
export const projectsApi = {
  getAll: () => api.get('/api/projects/'),
  getById: (id: string) => api.get(`/api/projects/${id}`),
  create: (data: any) => api.post('/api/projects/', data),
  update: (id: string, data: any) => api.put(`/api/projects/${id}`, data),
  delete: (id: string) => api.delete(`/api/projects/${id}`),
}

export const textsApi = {
  getByProject: (projectId: string) => api.get(`/api/projects/${projectId}/texts`),
  upload: (projectId: string, formData: FormData) => 
    apiClient.post(`/api/projects/${projectId}/texts/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }).then(response => response.data),
  delete: (projectId: string, textId: string) => 
    api.delete(`/api/projects/${projectId}/texts/${textId}`),
}

export const charactersApi = {
  getByText: (textId: string) => api.get(`/api/texts/${textId}/characters`),
  getById: (characterId: string) => 
    api.get(`/api/characters/${characterId}`),
  update: (characterId: string, data: any) => 
    api.put(`/api/characters/${characterId}`, data),
}

export const checklistApi = {
  getAll: (characterId?: number) => {
    const params = characterId ? { character_id: characterId } : {};
    return api.get('/api/checklists/', { params });
  },
  getChecklistForCharacter: (checklistSlug: string, characterId: number) =>
    api.get(`/api/checklists/${checklistSlug}/character/${characterId}`),
  createOrUpdateResponse: (data: {
    question_id: number;
    character_id: number;
    answer_id?: number;
    answer_text?: string;
    source_type?: 'FOUND_IN_TEXT' | 'LOGICALLY_DERIVED' | 'IMAGINED';
    comment?: string;
  }) => api.post('/api/checklists/responses', data),
  updateResponse: (responseId: number, data: {
    answer_id?: number;
    answer_text?: string;
    source_type?: 'FOUND_IN_TEXT' | 'LOGICALLY_DERIVED' | 'IMAGINED';
    comment?: string;
    change_reason?: string;
  }) => api.put(`/api/checklists/responses/${responseId}`, data),
  deleteResponse: (responseId: number, deleteReason?: string) =>
    api.delete(`/api/checklists/responses/${responseId}`, {
      params: deleteReason ? { delete_reason: deleteReason } : undefined
    }),
  getResponseHistory: (responseId: number) =>
    api.get(`/api/checklists/responses/${responseId}/history`),
  restoreResponseVersion: (responseId: number, data: {
    history_id: number;
    restore_reason?: string;
  }) => api.post(`/api/checklists/responses/${responseId}/restore`, data),
  getCharacterProgress: (characterId: number) =>
    api.get(`/api/checklists/character/${characterId}/progress`),
}

// API для работы с версионированием чеклистов
export const checklistVersionsApi = {
  getVersions: (checklistId: number) =>
    api.get(`/api/checklist-versions/${checklistId}/versions`),
  compareVersions: (checklistId: number, fromVersion: number, toVersion: number) =>
    api.get(`/api/checklist-versions/${checklistId}/compare/${fromVersion}/${toVersion}`),
  updateToLatest: (checklistId: number) =>
    api.post(`/api/checklist-versions/${checklistId}/update-to-latest`),
  migrateResponses: (checklistId: number, fromVersion: number, toVersion: number) =>
    api.post(`/api/checklist-versions/${checklistId}/migrate-responses`, {
      from_version: fromVersion,
      to_version: toVersion
    }),
  getUpdateStatus: (checklistId: number) =>
    api.get(`/api/checklist-versions/${checklistId}/update-status`),
  detectChanges: (checklistId: number) =>
    api.post(`/api/checklist-versions/${checklistId}/detect-changes`),
  getChangesSummary: (checklistId: number, fromVersion: number, toVersion: number) =>
    api.get(`/api/checklist-versions/${checklistId}/changes-summary/${fromVersion}/${toVersion}`),
  rollbackToVersion: (checklistId: number, targetVersion: number) =>
    api.post(`/api/checklist-versions/${checklistId}/rollback`, {
      target_version: targetVersion
    }),
  createSnapshot: (checklistId: number, description?: string) =>
    api.post(`/api/checklist-versions/${checklistId}/snapshot`, {
      description
    }),
  getEntityMatches: (checklistId: number, fromVersion: number, toVersion: number) =>
    api.get(`/api/checklist-versions/${checklistId}/entity-matches/${fromVersion}/${toVersion}`),
  previewMigration: (checklistId: number, fromVersion: number, toVersion: number) =>
    api.get(`/api/checklist-versions/${checklistId}/preview-migration/${fromVersion}/${toVersion}`)
}

export const exportApi = {
  // Экспорт персонажа в PDF или DOCX
  exportCharacter: (data: {
    character_id: number;
    format: 'pdf' | 'docx';
    export_type?: 'detailed' | 'summary' | 'compact';
    include_checklists?: string[];
    include_empty_responses?: boolean;
  }) => {
    return apiClient.post('/api/export/character', data, {
      responseType: 'blob', // Важно для получения бинарных данных
    }).then(response => {
      // Извлекаем имя файла из заголовков ответа
      const contentDisposition = response.headers['content-disposition'] || '';
      const fileNameMatch = contentDisposition.match(/filename=(.+)/);
      const fileName = fileNameMatch ? fileNameMatch[1].replace(/"/g, '') : 
        `character_export_${Date.now()}.${data.format}`;
      
      return {
        data: response.data,
        fileName,
        contentType: response.headers['content-type']
      };
    });
  },

  // Получить доступные форматы экспорта
  getFormats: () => api.get('/api/export/formats'),

  // Получить типы экспорта
  getTypes: () => api.get('/api/export/types'),

  // Получить шаблоны экспорта
  getTemplates: () => api.get('/api/export/templates'),

  // Массовый экспорт (если понадобится в будущем)
  exportMultipleCharacters: (data: {
    character_ids: number[];
    format: 'pdf' | 'docx';
    export_type?: 'detailed' | 'summary' | 'compact';
    merge_into_single_file?: boolean;
  }) => {
    return apiClient.post('/api/export/characters/bulk', data, {
      responseType: 'blob',
    }).then(response => {
      const contentDisposition = response.headers['content-disposition'] || '';
      const fileNameMatch = contentDisposition.match(/filename=(.+)/);
      const fileName = fileNameMatch ? fileNameMatch[1].replace(/"/g, '') : 
        `characters_export_${Date.now()}.${data.format}`;
      
      return {
        data: response.data,
        fileName,
        contentType: response.headers['content-type']
      };
    });
  }
}
