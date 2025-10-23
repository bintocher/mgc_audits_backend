# MGC Audits Backend

Backend система управления аудитами качества и несоответствиями для MGC. Заменяет существующую систему ISQ-AA и предоставляет расширенный функционал для планирования аудитов, управления несоответствиями и формирования отчетности.

## Возможности

- Планирование и ведение аудитов (4 типа графиков: product, process_system, lra, external)
- Управление несоответствиями (findings) с полным жизненным циклом
- Настраиваемый workflow статусов через визуальный конструктор
- Гибкая система ролей и прав доступа (RBAC)
- Многопредприятийная архитектура с изоляцией данных
- Интеграция с Active Directory, Yandex Mail, Telegram
- Автоматические уведомления (Email + Telegram)
- Отчетность с экспортом в Excel
- REST API для внешних систем
- Мультиязычность (русский, английский)

## Технологии

- **Язык:** Python 3.13
- **Фреймворк:** FastAPI (latest)
- **ORM:** SQLAlchemy 2.0+ (async support)
- **База данных:** PostgreSQL 18
- **Кеш/Очереди:** Redis 6.4+
- **Фоновые задачи:** Celery 5.5.3
- **Авторизация:** JWT (python-jose)
- **Валидация:** Pydantic 2.12.0+
- **Управление зависимостями:** uv + uvx

## Установка зависимостей

Зависимости устанавливаются автоматически при сборке Docker образа. Проект использует `uv` для управления зависимостями.

**Для локальной разработки:**

```bash
# Установка зависимостей из requirements.txt
pip install -r requirements.txt

# Или используя uv
uv pip install -r requirements.txt
```

**В Docker контейнере:**

```bash
# После docker-compose up
docker-compose exec backend pip install -r requirements.txt
```

## Настройка окружения

1. Создайте файл `.env` в корне проекта:

```bash
touch .env
```

2. Заполните необходимые переменные:

```env
# База данных PostgreSQL
DATABASE_URL=postgresql+asyncpg://mgc_audits:mgc_audits_password@postgres:5432/mgc_audits

# Redis для Celery
REDIS_URL=redis://redis:6379/0

# Безопасность
SECRET_KEY=your-secret-key-change-in-production-min-32-chars
SETTINGS_ENCRYPTION_KEY=your-32-byte-encryption-key!!

# JWT настройки
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Telegram Bot
TELEGRAM_BOT_TOKEN=your-telegram-bot-token

# Режим работы
ENVIRONMENT=development
DEBUG=True
```

**Важно:** 
- `SECRET_KEY` должен быть минимум 32 символа
- `SETTINGS_ENCRYPTION_KEY` должен быть ровно 32 байта
- Настройки интеграций (SMTP, LDAP, S3) управляются через таблицы в базе данных (`S3Storage`, `EmailAccount`, `LdapConnection`) и не должны храниться в `.env`

## Быстрый старт

### Предварительные требования

- Docker 24+
- Docker Compose 2.20+
- Git

### Установка и запуск

```bash
# 1. Клонировать репозиторий
git clone <repository-url>
cd backend

# 2. Создать файл .env
touch .env
# Заполните переменные окружения (см. Настройка окружения выше)

# 3. Собрать и запустить контейнеры
make build
make up

# 4. Инициализировать проект (создать миграции)
make init

# 5. Проверить работу
curl http://localhost:8000/health
```

Приложение будет доступно по адресу: http://localhost:8000

API документация: http://localhost:8000/docs

## Команды управления

Доступные команды через Makefile:

```bash
# Сборка и запуск
make build          # Собрать Docker образы
make up              # Запустить контейнеры
make down            # Остановить контейнеры
make restart         # Перезапустить контейнеры
make logs            # Показать логи всех сервисов
make clean           # Очистить контейнеры и volumes

# Миграции БД
make init            # Инициализировать проект (применить миграции)
make migrate         # Создать новую миграцию (использовать: make migrate msg="описание")
make upgrade         # Применить все миграции

# Разработка
make shell           # Войти в shell контейнера backend
```

### Работа с миграциями

```bash
# Создать миграцию
make migrate msg="добавить поле в таблицу audits"

# Применить миграции
make upgrade

# Откатить последнюю миграцию
docker-compose exec backend alembic downgrade -1
```

### Просмотр логов

```bash
# Все сервисы
make logs

# Только backend
docker-compose logs -f backend

# Только PostgreSQL
docker-compose logs -f postgres

# Только Celery worker
docker-compose logs -f celery_worker
```

## Структура проекта

```
backend/
├── app/
│   ├── api/              # API роутеры (FastAPI endpoints)
│   │   ├── auth.py       # Аутентификация
│   │   ├── users.py      # Пользователи
│   │   ├── audits.py     # Аудиты
│   │   ├── findings.py   # Несоответствия
│   │   └── ...
│   ├── core/             # Ядро приложения
│   │   ├── config.py     # Конфигурация
│   │   ├── security.py   # JWT, пароли
│   │   ├── database.py   # Подключение к БД
│   │   └── celery_worker.py # Celery конфигурация
│   ├── crud/             # CRUD операции
│   ├── models/           # SQLAlchemy модели
│   ├── schemas/          # Pydantic схемы
│   └── services/         # Бизнес-логика
│       ├── email.py      # Email отправка
│       ├── telegram_bot.py # Telegram бот
│       ├── tasks.py       # Celery задачи
│       └── ...
├── alembic/              # Миграции БД
├── scripts/               # Скрипты инициализации
├── requirements.txt       # Зависимости Python
├── pyproject.toml         # Конфигурация проекта
├── Dockerfile             # Docker образ
├── docker-compose.yml     # Docker Compose конфигурация
├── Makefile               # Команды управления
└── README.md              # Документация
```

## Архитектура

### Модульная структура

Приложение использует типичную для FastAPI структуру:

- **api/** - REST API endpoints, валидация запросов
- **core/** - Базовые компоненты (конфигурация, безопасность, БД)
- **crud/** - Операции с базой данных
- **models/** - SQLAlchemy ORM модели
- **schemas/** - Pydantic схемы для валидации
- **services/** - Бизнес-логика и фоновые задачи

### База данных

- **PostgreSQL 18** - основное хранилище данных
- **Redis** - кеширование и очереди для Celery
- **Alembic** - управление миграциями схемы БД

### Аутентификация и авторизация

- **JWT токены** - для API аутентификации
- **RBAC** - система ролей и прав доступа
- **Единая сессия** - пользователь может иметь только одну активную сессию

### Фоновые задачи

- **Celery Worker** - обработка асинхронных задач
- **Celery Beat** - периодические задачи (проверка квалификаций, отправка уведомлений)

## API Документация

После запуска приложения доступна интерактивная документация:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json

### Основные группы API

- `/api/v1/auth/*` - Аутентификация (login, refresh, logout, OTP, LDAP)
- `/api/v1/users/*` - Управление пользователями
- `/api/v1/roles/*` - Роли и права доступа
- `/api/v1/enterprises/*` - Предприятия
- `/api/v1/audits/*` - Аудиты
- `/api/v1/findings/*` - Несоответствия
- `/api/v1/reports/*` - Отчеты
- `/api/v1/notifications/*` - Уведомления
- `/api/v1/dashboard/*` - Дашборд

Полная спецификация API доступна в Swagger UI.

## Разработка

### Локальная разработка без Docker

```bash
# Установить зависимости
pip install -r requirements.txt

# Настроить .env
cp .env.example .env
# Отредактировать DATABASE_URL для локальной БД

# Запустить миграции
alembic upgrade head

# Запустить сервер
uvicorn app.main:app --reload
```

### Добавление новых моделей

```bash
# 1. Создать модель в app/models/
# 2. Создать схему в app/schemas/
# 3. Создать CRUD в app/crud/
# 4. Создать API роутер в app/api/
# 5. Зарегистрировать роутер в app/main.py
# 6. Создать миграцию
make migrate msg="добавить модель X"
```

### Тестирование

```bash
# Запустить тесты
pytest

# С покрытием
pytest --cov=app

# Конкретный тест
pytest tests/test_auth.py::test_login
```

Точка входа: `app/main.py`

## Безопасность

### Шифрование настроек

Критически важные настройки (пароли, API-ключи) шифруются в базе данных с использованием AES-256. Ключ шифрования хранится в переменной окружения `SETTINGS_ENCRYPTION_KEY`.

### Аутентификация

Поддерживаются следующие методы входа:

- **Email + пароль** - стандартная аутентификация
- **Email + OTP** - одноразовый пароль по email
- **LDAP/Active Directory** - сквозная авторизация для доменных пользователей

### Сессии

- Каждый пользователь может иметь только одну активную сессию
- При входе с нового устройства старая сессия становится недействительной
- JWT токены имеют ограниченное время жизни

### API токены

- Поддержка токенов для внешних систем
- Хеширование токенов перед сохранением в БД
- Возможность ротации токенов
- Ограничение по IP (whitelist)
- Rate limiting

## Интеграции

Настройки интеграций управляются через веб-интерфейс (таблицы в БД):

### Yandex Object Storage (S3)

- Хранение пользовательских файлов
- Pre-signed URLs для безопасного доступа
- Поддержка множественных подключений

### SMTP (Yandex Mail)

- Отправка уведомлений по email
- Поддержка множественных SMTP аккаунтов
- Роутинг по enterprise/division

### LDAP/Active Directory

- Сквозная авторизация
- Автоматический импорт пользователей
- Поддержка множественных подключений

### Telegram Bot

- Отправка уведомлений в Telegram
- Привязка через уникальную ссылку
- Опциональный канал уведомлений

## Развертывание на Production

### Требования к серверу

- Ubuntu 22/24 LTS
- Docker 24+ и Docker Compose 2.20+
- Nginx (рекомендуется)
- SSL сертификат

### Настройка Production окружения

1. **Настроить .env файл:**

```env
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=<strong-random-key>
SETTINGS_ENCRYPTION_KEY=<32-byte-key>
```

2. **Настроить Nginx:**

```nginx
server {
    listen 80;
    server_name api.example.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

3. **Настроить бэкапы PostgreSQL:**

```bash
# Ежедневный бэкап
0 2 * * * pg_dump mgc_audits > /backups/mgc_audits_$(date +\%Y\%m\%d).sql
```

4. **Мониторинг:**

- Настроить логирование
- Мониторинг ресурсов сервера
- Алерты при сбоях Celery

### Масштабирование

Для увеличения производительности:

- Добавить дополнительные Celery workers
- Настроить Redis Sentinel для высокой доступности
- Использовать PostgreSQL репликацию
- Настроить партиционирование таблиц (см. документацию)

## Поддержка

- **API документация:** http://localhost:8000/docs
- **Техническая документация:** см. файлы в `/docs`
- **Issues:** используйте систему Issues проекта

## Лицензия

Proprietary - Internal MGC use only

## Контакты

- **Проект:** MGC Audits Backend
- **Версия:** 0.1.0
- **Дата:** 2025