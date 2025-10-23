# MGC Audits Backend

Backend система управления аудитами качества и несоответствиями.

## Технологии

- Python 3.13
- FastAPI
- SQLAlchemy 2.0+ (async)
- PostgreSQL 18
- Redis 6.4
- Celery 5.5.3
- Alembic для миграций

## Установка зависимостей

Зависимости устанавливаются автоматически при сборке Docker образа. Проект использует `uv` для управления зависимостями:

```bash
# Все команды выполняются внутри Docker контейнера

# Установка зависимостей (после docker-compose up)
make install

# Установка конкретного пакета
docker-compose exec backend pip install package_name

# Запуск миграций
make upgrade
```

## Настройка окружения

Создайте файл `.env` на основе `.env.example`:

```bash
cp .env.example .env
```

Заполните необходимые переменные:

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/mgc_audits
REDIS_URL=redis://localhost:6379/0

SECRET_KEY=your-secret-key-here
SETTINGS_ENCRYPTION_KEY=your-encryption-key-here

DEBUG=True
ENVIRONMENT=development
```

**Важно:** Настройки интеграций (SMTP, LDAP, S3, Telegram) управляются через таблицы в базе данных `S3Storage`, `EmailAccount`, `LdapConnection` и не должны храниться в `.env`.

## Запуск через Docker Compose

```bash
# Собрать и запустить контейнеры
make build
make up

# Посмотреть логи
make logs

# Остановить контейнеры
make down
```

## Команды разработки

Все команды выполняются внутри Docker контейнеров:

```bash
# Собрать и запустить контейнеры
make build
make up

# Установить зависимости для разработки
make install-dev

# Инициализировать проект для разработки
make init-dev

# Создать миграцию
make migrate msg="описание миграции"

# Применить миграции
make upgrade

# Проверить код линтером
make lint

# Форматировать код
make format

# Запустить тесты
make test

# Войти в shell контейнера
make shell
```

## Структура проекта

```
backend/
├── app/
│   ├── api/          # API роутеры
│   ├── core/         # Конфигурация, безопасность
│   ├── crud/         # CRUD операции
│   ├── models/       # SQLAlchemy модели
│   ├── schemas/      # Pydantic схемы
│   └── services/    # Бизнес-логика
├── alembic/         # Миграции базы данных
├── main.py          # Точка входа
├── database.py      # Подключение к БД
└── requirements.txt # Зависимости
```

## API Документация

После запуска приложения доступна документация Swagger UI:
- http://localhost:8000/docs

## Лицензия

MIT
