// Конфигурация приложения
export const config = {
  // Авторизация
  authEnabled: false, // Флаг для включения/отключения авторизации
  
  // API
  apiBaseUrl: 'http://localhost:8000',
  
  // Mock пользователь для разработки (используется когда authEnabled = false)
  mockUser: {
    id: 1,
    username: 'dev_user',
    email: 'dev@example.com',
    is_active: true,
    is_superuser: false,
    created_at: new Date().toISOString()
  }
} 
