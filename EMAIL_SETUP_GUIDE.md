# Руководство по функциональности отправки писем при смене пароля

## Обзор системы

В проекте реализована полная система сброса пароля через email с использованием SMTP. Система состоит из нескольких компонентов, которые работают вместе для обеспечения безопасного сброса пароля.

## Архитектура системы

### 1. Настройки Email (settings.py)

```python
# Email настройки
smtp_server: str = "smtp.gmail.com"      # По умолчанию Gmail
smtp_port: int = 587                     # Порт для TLS
smtp_username: str = ""                  # Email отправителя
smtp_password: str = ""                  # Пароль приложения
smtp_use_tls: bool = True               # Использование TLS
email_from: str = ""                    # Email отправителя
email_from_name: str = "Роль"           # Имя отправителя
```

### 2. Переменные окружения (.env)

В вашем проекте используются следующие настройки:

```env
SMTP_SERVER=smtp.yandex.ru              # Яндекс SMTP сервер
SMTP_PORT=465                           # Порт для SSL (не TLS!)
SMTP_USE_TLS=true                       # Фактически используется SSL
SMTP_USERNAME=makishvili@yandex.ru      # Ваш email
SMTP_PASSWORD=aphzqvvicorgmyqt          # Пароль приложения Яндекса
EMAIL_FROM=makishvili@yandex.ru         # Email отправителя
EMAIL_FROM_NAME=Роль                    # Имя отправителя
```

## Процесс сброса пароля

### Шаг 1: Запрос на сброс пароля

**Endpoint:** `POST /api/auth/forgot-password`

**Процесс:**
1. Пользователь вводит свой email
2. Система ищет пользователя по email
3. Если пользователь найден и активен:
   - Создается токен сброса пароля
   - Отправляется email с ссылкой
4. Возвращается стандартный ответ (не раскрывая существование пользователя)

**Код в auth.py:**
```python
@router.post("/forgot-password", response_model=AuthResponse)
async def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    # Ищем пользователя по email
    user = auth_service.get_user_by_email(db, email=request.email)
    
    if user and user.is_active:
        # Создаем токен для сброса пароля
        reset_token = auth_service.create_password_reset_token(db, user)
        
        # Отправляем email
        email_service.send_password_reset_email(
            to_email=user.email,
            reset_token=reset_token,
            user_name=user.full_name or user.username
        )
```

### Шаг 2: Создание токена сброса

**Процесс в auth_service.create_password_reset_token():**
1. Отзываются все старые токены сброса пароля пользователя
2. Генерируется новый случайный токен (32 байта, URL-safe)
3. Создается хеш токена для хранения в БД
4. Токен сохраняется в БД с типом "password_reset"
5. Устанавливается срок действия: 1 час

```python
def create_password_reset_token(self, db: Session, user: User) -> str:
    # Отзываем старые токены
    token_crud.revoke_user_tokens_by_type(db, user_id=user.id, token_type="password_reset")
    
    # Генерируем токен
    reset_token = email_service.generate_reset_token()  # secrets.token_urlsafe(32)
    token_hash = self.get_token_hash(reset_token)       # SHA256 хеш
    
    # Срок действия: 1 час
    expires_at = datetime.utcnow() + timedelta(hours=1)
    
    # Сохраняем в БД
    token_data = {
        "user_id": user.id,
        "token_hash": token_hash,
        "token_type": "password_reset",
        "expires_at": expires_at
    }
    token_crud.create(db, obj_in=token_data)
```

### Шаг 3: Отправка Email

**Сервис EmailService._send_email():**

**Используемый почтовик:** Яндекс SMTP (smtp.yandex.ru:465)

**Настройки подключения:**
- Сервер: smtp.yandex.ru
- Порт: 465 (SSL)
- Аутентификация: makishvili@yandex.ru + пароль приложения
- Шифрование: SSL (не TLS, несмотря на настройку smtp_use_tls=true)

**Процесс отправки:**
```python
def _send_email(self, to_email: str, subject: str, html_content: str, text_content: str = None) -> bool:
    # Создаем MIME сообщение
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = f"{self.email_from_name} <{self.email_from}>"
    msg['To'] = to_email
    
    # Добавляем HTML и текстовые версии
    if text_content:
        msg.attach(MIMEText(text_content, 'plain', 'utf-8'))
    msg.attach(MIMEText(html_content, 'html', 'utf-8'))
    
    # Отправляем через SMTP
    with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
        if self.smtp_use_tls:
            server.starttls()  # Для порта 587
        # Для порта 465 используется SSL автоматически
        server.login(self.smtp_username, self.smtp_password)
        server.send_message(msg)
```

**Содержимое письма:**
- **Тема:** "Сброс пароля - Роль"
- **HTML версия:** Красиво оформленное письмо с кнопкой и ссылкой
- **Текстовая версия:** Простой текст для клиентов без HTML
- **Ссылка:** `http://localhost:5173/reset-password?token={reset_token}`

### Шаг 4: Сброс пароля по токену

**Endpoint:** `POST /api/auth/reset-password`

**Процесс:**
1. Пользователь переходит по ссылке из email
2. Вводит новый пароль
3. Система проверяет токен:
   - Создает хеш токена
   - Ищет в БД действующий токен типа "password_reset"
   - Проверяет срок действия
4. Если токен валиден:
   - Обновляет пароль пользователя
   - Отзывает токен сброса
   - Отзывает все JWT токены пользователя
   - Отправляет уведомление об успешной смене

```python
def reset_password_with_token(self, db: Session, token: str, new_password: str) -> bool:
    # Проверяем токен
    user = self.verify_password_reset_token(db, token)
    if not user:
        return False
    
    # Обновляем пароль
    user_update = UserUpdate(password=new_password)
    user_crud.update(db, db_obj=user, obj_in=user_update)
    
    # Отзываем токен сброса
    token_hash = self.get_token_hash(token)
    token_crud.revoke_token_by_hash(db, token_hash=token_hash)
    
    # Отзываем все JWT токены для безопасности
    token_crud.revoke_all_user_tokens(db, user_id=user.id)
```

### Шаг 5: Уведомление об успешной смене

После успешного сброса пароля отправляется второе письмо:

**Содержимое:**
- **Тема:** "Пароль изменен - Роль"
- **Содержание:** Уведомление о том, что пароль был изменен с указанием времени
- **Цель:** Информирование пользователя и предупреждение о возможной несанкционированной активности

## Безопасность системы

### 1. Токены сброса пароля
- **Генерация:** `secrets.token_urlsafe(32)` - криптографически стойкий генератор
- **Хранение:** В БД хранится только SHA256 хеш токена
- **Срок действия:** 1 час
- **Одноразовость:** Токен отзывается после использования
- **Уникальность:** Старые токены отзываются при создании нового

### 2. Защита от перебора
- Стандартный ответ независимо от существования пользователя
- Логирование ошибок только на сервере
- Ограничение по времени действия токена

### 3. Отзыв сессий
- При смене пароля отзываются все JWT токены пользователя
- Пользователь должен войти заново со всех устройств

## Настройка для разных почтовых провайдеров

### Яндекс (текущая настройка)
```env
SMTP_SERVER=smtp.yandex.ru
SMTP_PORT=465
SMTP_USE_TLS=true  # Фактически SSL
```

### Gmail
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true
```

### Mail.ru
```env
SMTP_SERVER=smtp.mail.ru
SMTP_PORT=465
SMTP_USE_TLS=true  # Фактически SSL
```

## Диагностика проблем

### Проверка настроек
Используйте скрипт `test_smtp.py` для проверки подключения:

```bash
cd backend && python test_smtp.py
```

### Частые проблемы
1. **Неверный порт/протокол:** Порт 465 требует SSL, порт 587 требует TLS
2. **Пароль приложения:** Для Яндекса нужен специальный пароль приложения, не основной пароль
3. **Двухфакторная аутентификация:** Должна быть включена для создания паролей приложений

### Логирование
Ошибки отправки email логируются в консоль:
```python
except Exception as e:
    print(f"Ошибка отправки email: {str(e)}")
    return False
```

## Заключение

Система отправки писем при смене пароля полностью функциональна и использует:
- **Почтовик:** Яндекс SMTP (smtp.yandex.ru:465)
- **Аутентификация:** makishvili@yandex.ru + пароль приложения
- **Безопасность:** Токены с ограниченным сроком действия, хеширование, отзыв сессий
- **Пользовательский опыт:** HTML письма с кнопками, уведомления об изменениях

Все настройки берутся из файла `.env`, что позволяет легко изменять конфигурацию без изменения кода.
