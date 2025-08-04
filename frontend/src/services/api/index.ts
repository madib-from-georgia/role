import axios, { AxiosInstance, AxiosRequestConfig } from 'axios'

const API_BASE_URL = 'http://localhost:8000'

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
  getByProject: (projectId: string) => api.get(`/api/projects/${projectId}/characters`),
  getById: (projectId: string, characterId: string) => 
    api.get(`/api/projects/${projectId}/characters/${characterId}`),
  create: (projectId: string, data: any) => 
    api.post(`/api/projects/${projectId}/characters`, data),
  update: (projectId: string, characterId: string, data: any) => 
    api.put(`/api/projects/${projectId}/characters/${characterId}`, data),
  delete: (projectId: string, characterId: string) => 
    api.delete(`/api/projects/${projectId}/characters/${characterId}`),
  analyze: (projectId: string, characterId: string) => 
    api.post(`/api/projects/${projectId}/characters/${characterId}/analyze`),
}
