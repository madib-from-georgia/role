# Скрипты для управления проектом

## 🔐 Управление авторизацией

### Основной скрипт: `toggle-auth.sh`

Удобный скрипт для полного управления авторизацией в проекте.

#### Команды:
```bash
./scripts/toggle-auth.sh status     # Показать текущее состояние
./scripts/toggle-auth.sh enable     # Включить авторизацию
./scripts/toggle-auth.sh disable    # Отключить авторизацию
./scripts/toggle-auth.sh restart    # Перезапустить сервисы
./scripts/toggle-auth.sh help       # Показать справку
```

#### Примеры использования:
```bash
# Проверить состояние
./scripts/toggle-auth.sh status

# Отключить авторизацию для разработки
./scripts/toggle-auth.sh disable

# Включить авторизацию для production
./scripts/toggle-auth.sh enable

# Перезапустить сервисы после изменения
./scripts/toggle-auth.sh restart
```

### Быстрый переключатель: `quick-auth-toggle.sh`

Автоматически переключает между включенной и отключенной авторизацией.

```bash
./scripts/quick-auth-toggle.sh
```

## 🚀 Запуск сервисов

### Backend (FastAPI)
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

### Frontend (React)
```bash
cd frontend
npm run dev
```

## 📋 Состояния авторизации

### 🔴 Авторизация включена
- **Backend**: `auth_enabled: bool = True`
- **Frontend**: `authEnabled: true`
- **Поведение**: Все API запросы требуют JWT токены
- **Использование**: Production, тестирование безопасности

### 🟢 Авторизация отключена
- **Backend**: `auth_enabled: bool = False`
- **Frontend**: `authEnabled: false`
- **Поведение**: Все API запросы работают без токенов
- **Использование**: Разработка, демонстрация, тестирование

## ⚠️ Важные замечания

1. **После изменения конфигурации обязательно перезапустите сервисы**
2. **В production всегда включайте авторизацию**
3. **Mock пользователь создается автоматически при отключенной авторизации**
4. **Все изменения делаются в конфигурационных файлах**

## 🔧 Технические детали

### Файлы конфигурации:
- **Backend**: `backend/app/config/settings.py`
- **Frontend**: `frontend/src/config.ts`

### Mock пользователь (при отключенной авторизации):
- **ID**: 1
- **Username**: `dev_user`
- **Email**: `dev@example.com`
- **Password**: `dev_password_123`

## 🆘 Решение проблем

### Ошибка 401 Unauthorized
```bash
# Отключить авторизацию
./scripts/toggle-auth.sh disable

# Перезапустить сервисы
./scripts/toggle-auth.sh restart
```

### Проверка состояния
```bash
./scripts/toggle-auth.sh status
```

### Сброс к состоянию по умолчанию
```bash
./scripts/toggle-auth.sh disable
./scripts/toggle-auth.sh restart
```

---

*Скрипты автоматически определяют ОС и используют соответствующие команды sed*
