# Digitalizer

Сервис для генерации документов из шаблонов.

|     Роль     |             Участник              |
|--------------|-----------------------------------|
| **Backend**  | Валиуллин Азат, Минахметов Камиль |
| **Frontend** | Юнусов Артем                      |

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
git clone https://github.com/ItisDigitalizer/backend.git
cd backend

# Установи uv (если ещё не)
pip install uv

# Создай виртуальное окружение и установи зависимости
uv sync


## ⚙️ Переменные окружения

Создай файл `.env` в корне проекта:

```env
DATABASE_URL=...
```

## 🚀 Запуск

```bash
# Примени миграции
alembic upgrade head

# Запусти сервер
uv run fastapi dev
```

Открой http://localhost:8000/docs — там Swagger UI со всеми эндпоинтами.


## 📌 Модели и связи

| Модель | Поля | Связи |
|--------|------|-------|
| **User** | username, email, password, role | → templates, processes |
| **DocumentTemplate** | name, description, user_id, file_path | → user, fields, processes |
| **TemplateField** | template_id, name, description | → template |
| **GenerationProcess** | user_id, template_id | → user, template, documents |
| **GeneratedDocument** | gen_process_id, file_path | → process |

Все модели имеют `id` (UUID), `created_at`, `updated_at` (TIMESTAMP WITH TIME ZONE).
