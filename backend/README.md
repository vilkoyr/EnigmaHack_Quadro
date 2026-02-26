# Backend — система обработки обращений

Django + Django REST Framework + JWT. Модели данных и REST API по ТЗ.

- **Swagger:** [http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/) (после запуска сервера).
- **БД:** локально — SQLite, на проде — PostgreSQL (через переменные окружения).
- **Docker:** два сервиса — backend и PostgreSQL (см. [DEPLOY.md](DEPLOY.md)).

## Установка

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser  # первый пользователь — задайте username/email/password
```

Роль по умолчанию у пользователей — `viewer`. Чтобы сделать первого пользователя админом:

```bash
python manage.py shell
>>> from core.models import User
>>> u = User.objects.get(username='admin')
>>> u.role = 'admin'
>>> u.save()
```

## Запуск

```bash
python manage.py runserver
```

API: `http://127.0.0.1:8000/api/`  
Документация API (Swagger): `http://127.0.0.1:8000/api/docs/`

Подробные инструкции: **локальный запуск** и **запуск на проде** (в т.ч. Docker) — в [DEPLOY.md](DEPLOY.md).

## Модели (Django)

- **User** — кастомная модель (AbstractUser) с полем `role`: admin, agent, viewer.
- **UserProfile** — OneToOne: phone_number, department, avatar, telegram_id, slack_webhook.
- **EmailMessage** — исходные письма (message_id, subject, body_plain/html, sender_*, device_serial_numbers, received_at, attachments, raw_headers).
- **ProcessedData** — результат обработки + техподдержка (email OneToOne, full_name, object, phone, serial_numbers, sentiment, category, generated_response, status, assignee, internal_notes, client_feedback и др.).
  - Доп. поля веб-таблицы: `device_type` (тип/модель прибора), `question_summary` (суть вопроса), `sentiment` (positive/neutral/negative).
- **Comment** — комментарии к обращению (processed_data, author, text, is_internal).
- **KnowledgeBase** — база знаний (title, content, content_type, keywords).
- **KnowledgeEmbedding** — эмбеддинги для векторного поиска (JSONField; для pgvector можно заменить на VectorField).
- **ProcessingLog** — логи обработки писем агентом.

## API Endpoints

### Аутентификация

| Метод | URL | Описание |
|-------|-----|----------|
| POST | `/api/auth/register/` | Регистрация (только админ или все — `REGISTRATION_OPEN_TO_ALL`) |
| POST | `/api/auth/login/` | JWT access + refresh |
| POST | `/api/auth/logout/` | Выход (клиент удаляет токен) |
| POST | `/api/auth/refresh/` | Обновление access-токена |
| GET  | `/api/auth/profile/` | Профиль текущего пользователя |
| PUT  | `/api/auth/profile/` | Обновление профиля |
| POST | `/api/auth/change-password/` | Смена пароля (old_password, new_password) |

### Обращения (Processed Data)

| Метод | URL | Описание |
|-------|-----|----------|
| GET    | `/api/processed/` | Список (фильтры: status, category, sentiment, assignee, date_from, date_to; пагинация) |
| GET    | `/api/processed/<id>/` | Детали |
| PUT    | `/api/processed/<id>/` | Редактирование (админ или назначенный агент) |
| DELETE | `/api/processed/<id>/` | Удаление (только админ) |
| PATCH  | `/api/processed/<id>/assign/` | Назначить ответственного (body: `user_id` для админа) |
| PATCH  | `/api/processed/<id>/status/` | Изменить статус (body: `status`) |
| GET    | `/api/processed/<id>/comments/` | Список комментариев (viewer видит только не internal) |
| POST   | `/api/processed/<id>/comments/` | Добавить комментарий (body: text, is_internal) |
| DELETE | `/api/processed/<id>/comments/<comment_id>/` | Удалить комментарий (автор или админ) |

### Экспорт

| Метод | URL | Описание |
|-------|-----|----------|
| POST | `/api/export/` | Экспорт в CSV или XLSX (body/query: format, status, category, sentiment, assignee, date_from, date_to) |

### База знаний

| Метод | URL | Описание |
|-------|-----|----------|
| GET    | `/api/knowledge/` | Список статей |
| POST   | `/api/knowledge/` | Создание |
| GET    | `/api/knowledge/<id>/` | Детали |
| PUT    | `/api/knowledge/<id>/` | Редактирование |
| DELETE | `/api/knowledge/<id>/` | Удаление |

### Сотрудники (только admin)

| Метод | URL | Описание |
|-------|-----|----------|
| GET    | `/api/users/` | Список (фильтр: role, department) |
| GET    | `/api/users/<id>/` | Детали |
| PUT    | `/api/users/<id>/` | Редактирование |
| DELETE | `/api/users/<id>/` | Деактивация (is_active=False) |

### Обработка письма (опционально)

| Метод | URL | Описание |
|-------|-----|----------|
| POST | `/api/process-email/` | Запуск обработки (body: email_id или text). Заглушка под интеграцию с агентом. |

## Настройки (config/settings.py)

- `REGISTRATION_OPEN_TO_ALL` — если True, регистрация доступна всем (роль = viewer).
- `AUTH_USER_MODEL = 'core.User'` — кастомная модель пользователя.
- БД по умолчанию — SQLite; для PostgreSQL замените `DATABASES` в settings.py.

## Статусы обращений (ProcessedData.status)

- `new` — новое  
- `in_progress` — в работе  
- `waiting_for_client` — ожидает ответа клиента  
- `resolved` — решено  
- `closed` — закрыто  
