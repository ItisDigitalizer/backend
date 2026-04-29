# Digitalizer

Сервис для генерации документов из шаблонов.

## 🛠 Стек

- **FastAPI** — веб-фреймворк
- **SQLModel** + **SQLAlchemy 2.0** — ORM и модели
- **PostgreSQL** — база данных
- **Alembic** — миграции
- **Pydantic v2** — валидация данных
- **Loguru** — логирование

## 📦 Установка

```bash
# Клонируй репозиторий
git clone https://github.com/your-username/digitalizer.git
cd digitalizer

# Установи uv (если ещё не)
pip install uv

# Создай виртуальное окружение и установи зависимости
uv sync

# Активируй окружение
# Windows:
.venv\Scripts\activate
# Linux/MacOS:
source .venv/bin/activate
```

## ⚙️ Переменные окружения

Создай файл `.env` в корне проекта:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/digitalizer
```

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `DATABASE_URL` | URL подключения к PostgreSQL | `postgresql+asyncpg://postgres:postgres@localhost:5432/digitalizer` |
| `APP_HOST` | Хост сервера | `0.0.0.0` |
| `APP_PORT` | Порт сервера | `8000` |
| `LOG_LEVEL` | Уровень логирования | `INFO` |
| `DEBUG` | Режим отладки | `False` |

## 🚀 Запуск

```bash
# Примени миграции
alembic upgrade head

# Запусти сервер
fastapi dev app/main.py
or
uv run fastapi dev
```

Открой http://localhost:8000/docs — там Swagger UI со всеми эндпоинтами.

## 📁 Структура проекта

```
app/
├── core/           # Конфигурация, подключение к БД
├── db/             # Сессии БД
├── models/         # SQLModel модели и Pydantic схемы
│   ├── base.py                 # Базовая модель с id, created_at, updated_at
│   ├── user.py                 # User (модель, Create, Update, Read)
│   ├── document_template.py    # DocumentTemplate (модель, Create, Update, Read)
│   ├── template_field.py       # TemplateField (модель, Create, Update, Read)
│   ├── generation_process.py   # GenerationProcess (модель, Create, Update, Read)
│   └── generated_document.py   # GeneratedDocument (модель, Create, Update, Read)
├── repositories/   # Доступ к данным (CRUD)
│   ├── base.py
│   ├── user_repo.py
│   ├── document_template_repo.py
│   ├── template_field_repo.py
│   ├── generation_process_repo.py
│   └── generated_document_repo.py
├── services/       # Бизнес-логика
│   ├── base.py
│   ├── user_service.py
│   ├── document_template_service.py
│   ├── template_field_service.py
│   ├── generation_process_service.py
│   └── generated_document_service.py
├── routers/        # FastAPI роутеры
│   ├── users.py
│   ├── document_template.py
│   ├── template_field.py
│   ├── generation_process.py
│   └── generated_document.py
├── dependencies.py # DI-зависимости
└── main.py         # Точка входа
migrations/         # Файлы миграций Alembic
```

## 📌 Модели и связи

| Модель | Поля | Связи |
|--------|------|-------|
| **User** | username, email, password, role | → templates, processes |
| **DocumentTemplate** | name, description, user_id, file_path | → user, fields, processes |
| **TemplateField** | template_id, name, description | → template |
| **GenerationProcess** | user_id, template_id | → user, template, documents |
| **GeneratedDocument** | gen_process_id, file_path | → process |

Все модели имеют `id` (UUID), `created_at`, `updated_at` (TIMESTAMP WITH TIME ZONE).

## 🔗 API (v1)

### Пользователи
| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/api/v1/users/` | Создать пользователя |
| GET | `/api/v1/users/` | Список пользователей |
| GET | `/api/v1/users/{id}` | Получить пользователя |
| PATCH | `/api/v1/users/{id}` | Обновить пользователя |
| DELETE | `/api/v1/users/{id}` | Удалить пользователя |

### Шаблоны документов
| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/api/v1/templates/` | Создать шаблон |
| GET | `/api/v1/templates/` | Список шаблонов |
| GET | `/api/v1/templates/{id}` | Получить шаблон |
| PATCH | `/api/v1/templates/{id}` | Обновить шаблон |
| DELETE | `/api/v1/templates/{id}` | Удалить шаблон |

### Поля шаблонов
| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/api/v1/fields/` | Создать поле |
| GET | `/api/v1/fields/` | Список полей |
| GET | `/api/v1/fields/{id}` | Получить поле |
| PATCH | `/api/v1/fields/{id}` | Обновить поле |
| DELETE | `/api/v1/fields/{id}` | Удалить поле |

### Процессы генерации
| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/api/v1/processes/` | Создать процесс |
| GET | `/api/v1/processes/` | Список процессов |
| GET | `/api/v1/processes/{id}` | Получить процесс |
| PATCH | `/api/v1/processes/{id}` | Обновить процесс |
| DELETE | `/api/v1/processes/{id}` | Удалить процесс |

### Сгенерированные документы
| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/api/v1/documents/` | Создать документ |
| GET | `/api/v1/documents/` | Список документов |
| GET | `/api/v1/documents/{id}` | Получить документ |
| PATCH | `/api/v1/documents/{id}` | Обновить документ |
| DELETE | `/api/v1/documents/{id}` | Удалить документ |
| DELETE | `/api/v1/documents/by-process/{id}` | Удалить документы процесса |
