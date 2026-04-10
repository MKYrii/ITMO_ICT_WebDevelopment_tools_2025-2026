# Отчет по практикам и лабораторной работе 1

Выполнил: Михайлов Юрий, К3341  

---

- Пулл-реквест: *https://github.com/TonikX/ITMO_ICT_WebDevelopment_tools_2025-2026/pull/23*

---

## Практические работы 1.1-1.3

### Практика 1.1 
- Пошагово реализованы проект и методы, описанные в практике
- Созданы для временной базы данных модели и API для профессий

### Практика 1.2 
- Пошагово реализованы проект и методы, описанные в практике
- Созданы API и модели для умений воинов и их ассоциативной сущности, вложено отображать умения при запросе воина

### Практика 1.3 
- Реализованы все улучшения:
  - Добавлены `alembic.ini` и `migrations/*`.
  - Настроено чтение `DB_URL` из `.env`.
  - Добавлены `.env.example` и `.gitignore` с исключением env-файлов.

---

## Лабораторная работа 1 (задание на 15 баллов)

### Используемый стек
- FastAPI
- SQLModel
- SQLite
- Alembic
- JWT (PyJWT)
- Хэширование паролей

### Модели

Файл: `app/models.py`

- `User`
- `Task`
- `Tag`
- `UserTaskAssignment` (ассоциативная сущность User ↔ Task)
- `TaskTag` (ассоциативная сущность Task ↔ Tag)

Также используются Enum типы:
- `TaskPriority` (low, medium, high)
- `TaskStatus` (todo, in_progress, done)

#### Выполнение критериев по структуре БД
- Таблиц: **5** (требование: 5+).
- `one-to-many`: `User → Task` (владелец задачи).
- `many-to-many`: `User ↔ Task` через `UserTaskAssignment`.
- `many-to-many`: `Task ↔ Tag` через `TaskTag`.
- Ассоциативная сущность `UserTaskAssignment` содержит поле связи `comment` (кроме FK).
- Ассоциативная сущность `TaskTag` содержит поле связи `is_primary` (кроме FK).

---

## Подключение к БД

Файл: `app/db.py`

```python
from sqlmodel import SQLModel, Session, create_engine
from app.core.config import DB_URL

engine = create_engine(DB_URL, echo=True)

def init_db() -> None:
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
```

## Pydantic-схемы

Файл: `app/schemas.py`

Все схемы разделены по функциональному признаку и используют наследование для избежания дублирования кода.

### Базовые перечисления
- `TaskStatus` (todo, in_progress, done)
- `TaskPriority` (low, medium, high)

### User-схемы
- `UserBase` — базовые поля (email, full_name)
- `UserCreate` — регистрация (наследует UserBase + password)
- `UserRead` — ответ сервера (добавляет id, is_active, created_at)
- `UserUpdate` — обновление данных (все поля опциональны)
- `PasswordChange` — смена пароля (old_password, new_password)
- `LoginRequest` — вход в систему (username, password)
- `TokenResponse` — JWT токен (access_token, token_type)

### Tag-схемы
- `TagBase` — базовые поля (name, color)
- `TagCreate` — создание тега
- `TagResponse` — ответ с id
- `TagUpdate` — обновление (опциональные поля)

### Task-схемы
- `TaskBase` — базовые поля задачи (title, description, deadline, priority, status, estimated_minutes, recurrence_rule)
- `TaskCreate` — создание задачи (наследует TaskBase)
- `TaskUpdate` — обновление (все поля опциональны)
- `TaskResponse` — ответ с id, owner_user_id, created_at
- `TaskListResponse` — пагинированный список задач (tasks + total)

### UserTaskAssignment-схемы
- `TaskAssignmentCreate` — назначение пользователя (task_id, user_id, comment)
- `TaskAssignmentResponse` — ответ с id, assigned_at и связанными данными

### TaskTag-схемы
- `TaskTagCreate` — привязка тега к задаче (task_id, tag_id, is_primary)
- `TaskTagResponse` — ответ с информацией о связи и вложенным объектом тега

### Особенности реализации
- Использован `from_attributes = True` для совместимости с SQLModel (режим ORM).
- Применен `model_rebuild()` для разрешения циклических ссылок между `TaskResponse` и `UserResponse`.
- Все enum-поля типизированы соответствующими перечислениями из models.py.
- Опциональные поля помечены `Optional` с дефолтным значением `None`.

---

## API эндпоинты 

### Users
- `POST /users/register` — регистрация пользователя.
- `GET /users/me` — данные текущего пользователя.
- `GET /users/` — список всех пользователей.
- `GET /users/{user_id}` — получить пользователя по ID.
- `PATCH /users/{user_id}` — обновить данные пользователя.
- `PATCH /users/change-password` — смена пароля.

### Tasks
- `POST /tasks/` — создать задачу.
- `GET /tasks/` — список задач текущего пользователя (с фильтрацией по статусу и приоритету).
- `GET /tasks/{task_id}` — получить задачу.
- `PATCH /tasks/{task_id}` — обновить задачу.
- `DELETE /tasks/{task_id}` — удалить задачу.

### Tags
- `POST /tags/` — создать тег.
- `GET /tags/` — список всех тегов.
- `GET /tags/{tag_id}` — получить тег.
- `PATCH /tags/{tag_id}` — обновить тег.
- `DELETE /tags/{tag_id}` — удалить тег.

### TaskTags (связь задач и тегов)
- `POST /task-tags/` — привязать тег к задаче (с флагом `is_primary`).
- `GET /task-tags/task/{task_id}` — получить все теги задачи.
- `GET /task-tags/tag/{tag_id}` — получить все задачи с указанным тегом.
- `DELETE /task-tags/{task_id}/{tag_id}` — отвязать тег от задачи.

### Assignments (назначение пользователей на задачи)
- `POST /assignments/` — назначить пользователя на задачу (с комментарием).
- `GET /assignments/task/{task_id}` — получить всех назначенных на задачу пользователей.
- `GET /assignments/user/{user_id}` — получить все задачи, назначенные пользователю.
- `DELETE /assignments/{task_id}/{user_id}` — снять назначение пользователя с задачи.

---

## Реализация требований на 15 баллов

- Регистрация и авторизация пользователей.
- Генерация JWT токена.
- Аутентификация по JWT (через dependency `get_current_user`).
- Хэширование паролей.
- API для:
  - информации о текущем пользователе,
  - списка пользователей,
  - получения пользователя по ID,
  - обновления пользователя,
  - смены пароля.

---

## Миграции и окружение

- Конфигурация Alembic: `alembic.ini`, `migrations/*`.
- Начальная миграция: `migrations/versions/0001_initial.py`.
- .env файл:
  - исключение env: `.gitignore`,
  - использование при чтении глобальных переменных.

---

## Вывод

В ходе выполнения лабораторной работы разработано серверное приложение — система тайм-менеджмента с авторизацией и управлением задачами.

Спроектирована база данных на SQLite, реализована модульная структура FastAPI с разделением на модели, схемы, роутеры и зависимости. Создана система аутентификации: регистрация, JWT-токены, хэширование паролей. Написаны CRUD-операции для всех сущностей с фильтрацией, назначением пользователей и тегами. Выполнены миграции через Alembic, настроено окружение через `.env`. Подготовлена документация в MkDocs с деплоем на GitHub Pages.
