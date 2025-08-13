/**
 * Утилиты для обработки ошибок API
 */

export interface ApiError {
  detail: string
  code?: string
  status: number
}

/**
 * Маппинг сообщений об ошибках для лучшего UX
 */
export const ERROR_MESSAGES = {
  // Общие ошибки сети
  NETWORK_ERROR: 'Проблемы с подключением к серверу. Проверьте интернет-соединение.',
  SERVER_ERROR: 'Внутренняя ошибка сервера. Попробуйте позже.',
  
  // Ошибки аутентификации
  INVALID_CREDENTIALS: 'Неверный email или пароль',
  USER_NOT_FOUND: 'Пользователь с таким email не найден. Возможно, вам нужно зарегистрироваться?',
  USER_INACTIVE: 'Аккаунт деактивирован. Обратитесь к администратору.',
  
  // Ошибки регистрации
  EMAIL_ALREADY_EXISTS: 'Пользователь с таким email уже существует',
  USERNAME_ALREADY_EXISTS: 'Пользователь с таким именем уже существует',
  
  // Ошибки валидации
  INVALID_EMAIL: 'Неверный формат email адреса',
  PASSWORD_TOO_SHORT: 'Пароль должен содержать минимум 8 символов',
  WEAK_PASSWORD: 'Пароль слишком простой. Используйте буквы, цифры и специальные символы.',
  
  // Ошибки токенов
  TOKEN_EXPIRED: 'Сессия истекла. Пожалуйста, войдите снова.',
  INVALID_TOKEN: 'Недействительный токен. Пожалуйста, войдите снова.',
  
  // Дефолтные сообщения
  UNKNOWN_ERROR: 'Произошла неизвестная ошибка. Попробуйте позже.',
} as const

/**
 * Проверяет валидность email адреса
 */
export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
  return emailRegex.test(email.trim())
}

/**
 * Проверяет силу пароля
 */
export const validatePassword = (password: string): { isValid: boolean; message?: string } => {
  if (password.length < 8) {
    return { isValid: false, message: ERROR_MESSAGES.PASSWORD_TOO_SHORT }
  }
  
  // Проверяем, что пароль содержит хотя бы одну букву и одну цифру
  const hasLetter = /[a-zA-Z]/.test(password)
  const hasNumber = /\d/.test(password)
  
  if (!hasLetter || !hasNumber) {
    return { isValid: false, message: ERROR_MESSAGES.WEAK_PASSWORD }
  }
  
  return { isValid: true }
}

/**
 * Обрабатывает ошибки API и возвращает понятное пользователю сообщение
 */
export const handleApiError = (error: unknown): string => {
  // Type guards для работы с unknown
  const isErrorWithResponse = (err: unknown): err is { response: { status: number; data?: { detail?: string } } } => {
    return typeof err === 'object' && err !== null && 'response' in err;
  }
  
  const isErrorWithStatus = (err: unknown): err is { status: number } => {
    return typeof err === 'object' && err !== null && 'status' in err;
  }
  
  const isErrorWithCode = (err: unknown): err is { code: string } => {
    return typeof err === 'object' && err !== null && 'code' in err;
  }
  
  const isErrorWithDetail = (err: unknown): err is { detail: string } => {
    return typeof err === 'object' && err !== null && 'detail' in err;
  }
  
  // Если это сетевая ошибка
  if (!isErrorWithResponse(error) && isErrorWithCode(error) && error.code === 'NETWORK_ERROR') {
    return ERROR_MESSAGES.NETWORK_ERROR
  }
  
  // Если это ошибка fetch API
  if (error instanceof TypeError && error.message.includes('fetch')) {
    return ERROR_MESSAGES.NETWORK_ERROR
  }
  
  // Получаем детали ошибки (учитываем разные форматы)
  const status = isErrorWithResponse(error) ? error.response.status :
               isErrorWithStatus(error) ? error.status : 0
  const detail = isErrorWithResponse(error) ? error.response.data?.detail || '' :
                isErrorWithDetail(error) ? error.detail :
                error instanceof Error ? error.message : ''
  
  // Маппинг по статус кодам
  switch (status) {
    case 401:
      if (detail.includes('email') || detail.includes('пароль')) {
        return ERROR_MESSAGES.INVALID_CREDENTIALS
      }
      if (detail.includes('токен') || detail.includes('token')) {
        return ERROR_MESSAGES.TOKEN_EXPIRED
      }
      return ERROR_MESSAGES.INVALID_CREDENTIALS
      
    case 400:
      if (detail.includes('email уже существует')) {
        return ERROR_MESSAGES.EMAIL_ALREADY_EXISTS
      }
      if (detail.includes('username уже существует')) {
        return ERROR_MESSAGES.USERNAME_ALREADY_EXISTS
      }
      if (detail.includes('email')) {
        return ERROR_MESSAGES.INVALID_EMAIL
      }
      return detail || ERROR_MESSAGES.UNKNOWN_ERROR
      
    case 403:
      return ERROR_MESSAGES.USER_INACTIVE
      
    case 404:
      if (detail.includes('пользователь') || detail.includes('user')) {
        return ERROR_MESSAGES.USER_NOT_FOUND
      }
      return detail || ERROR_MESSAGES.UNKNOWN_ERROR
      
    case 422:
      // Ошибки валидации
      return detail || ERROR_MESSAGES.UNKNOWN_ERROR
      
    case 500:
    case 502:
    case 503:
    case 504:
      return ERROR_MESSAGES.SERVER_ERROR
      
    default:
      // Пытаемся использовать сообщение с сервера, если оно понятное
      if (detail && detail.length > 0 && detail.length < 200) {
        return detail
      }
      return ERROR_MESSAGES.UNKNOWN_ERROR
  }
}

/**
 * Создает специфичное для аутентификации сообщение об ошибке
 */
export const handleAuthError = (error: unknown): string => {
  const isErrorWithResponse = (err: unknown): err is { response: { status: number; data?: { detail?: string } } } => {
    return typeof err === 'object' && err !== null && 'response' in err;
  }
  
  const isErrorWithStatus = (err: unknown): err is { status: number } => {
    return typeof err === 'object' && err !== null && 'status' in err;
  }
  
  const isErrorWithDetail = (err: unknown): err is { detail: string } => {
    return typeof err === 'object' && err !== null && 'detail' in err;
  }
  
  const status = isErrorWithResponse(error) ? error.response.status :
               isErrorWithStatus(error) ? error.status : 0
  const detail = isErrorWithResponse(error) ? error.response.data?.detail || '' :
                isErrorWithDetail(error) ? error.detail :
                error instanceof Error ? error.message : ''
  
  // Специальная обработка для 401 в контексте входа
  if (status === 401) {
    // Если сообщение содержит информацию о регистрации
    if (detail.includes('не найден') || detail.includes('not found')) {
      return 'Пользователь с таким email не найден. Проверьте email или зарегистрируйтесь.'
    }
    return ERROR_MESSAGES.INVALID_CREDENTIALS
  }
  
  return handleApiError(error)
}

/**
 * Создает специфичное для регистрации сообщение об ошибке
 */
export const handleRegistrationError = (error: unknown): string => {
  const isErrorWithResponse = (err: unknown): err is { response: { data?: { detail?: string } } } => {
    return typeof err === 'object' && err !== null && 'response' in err;
  }
  
  const isErrorWithDetail = (err: unknown): err is { detail: string } => {
    return typeof err === 'object' && err !== null && 'detail' in err;
  }
  
  const detail = isErrorWithResponse(error) ? error.response.data?.detail || '' :
                isErrorWithDetail(error) ? error.detail :
                error instanceof Error ? error.message : ''
  
  if (detail.includes('email уже существует')) {
    return 'Пользователь с таким email уже зарегистрирован. Попробуйте войти или восстановить пароль.'
  }
  
  if (detail.includes('username уже существует')) {
    return 'Пользователь с таким именем уже существует. Выберите другое имя пользователя.'
  }
  
  return handleApiError(error)
}
