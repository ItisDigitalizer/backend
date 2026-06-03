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

...

Впиши настройки SMTP и адрес фронтенда

SMTP__USERNAME=your_email@example.com
SMTP__PASSWORD=your_password
SMTP__MAIL_FROM=your_email@example.com

...

FRONTEND__URL=
```

## 🚀 Запуск

```bash
# Примени миграции
uv alembic upgrade head

# Запусти сервер
uv run fastapi dev
```

Открой http://localhost:8000/docs — там Swagger UI со всеми эндпоинтами.


## 📌 Модели и связи

| Модель | Поля | Связи                                                 |
|--------|------|-------------------------------------------------------|
| **User** | username, email, password, role, is_verified (bool) | → templates, processes, sessions, email_notifications |
| **DocumentTemplate** | name, description, user_id, file_path | → user, fields, processes                             |
| **TemplateField** | template_id, name, description | → template                                            |
| **GenerationProcess** | user_id, template_id | → user, template, documents                           |
| **GeneratedDocument** | gen_process_id, file_path | → process                                             |
| **EmailNotification** | id, created_at, updated_at, recipient, subject, template_name, status, user_id | → user                                                |

Все модели имеют `id` (UUID), `created_at`, `updated_at` (TIMESTAMP WITH TIME ZONE).
