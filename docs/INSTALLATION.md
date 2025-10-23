# Инструкция по установке MGC Audits Backend

## Содержание

1. [Предварительные требования](#предварительные-требования)
2. [Установка через Docker](#установка-через-docker)
3. [Локальная установка](#локальная-установка)
4. [Настройка базы данных](#настройка-базы-данных)
5. [Настройка интеграций](#настройка-интеграций)
6. [Проверка установки](#проверка-установки)
7. [Устранение неполадок](#устранение-неполадок)

## Предварительные требования

### Системные требования

- **ОС:** Linux (Ubuntu 22/24 LTS), macOS, или Windows с WSL2
- **Docker:** версия 24.0.0 или выше
- **Docker Compose:** версия 2.20.0 или выше
- **Память:** минимум 4 GB RAM
- **Диск:** минимум 10 GB свободного места

### Проверка установки Docker

```bash
# Проверить версию Docker
docker --version

# Проверить версию Docker Compose
docker-compose --version
```

Если Docker не установлен, установите его согласно официальной документации:
- Linux: https://docs.docker.com/engine/install/ubuntu/
- macOS: https://docs.docker.com/desktop/install/mac-install/
- Windows: https://docs.docker.com/desktop/install/windows-install/

## Установка через Docker

### Шаг 1: Клонирование репозитория

```bash
git clone <repository-url>
cd mgc_audits/backend
```

### Шаг 2: Создание файла конфигурации

Создайте файл `.env` в корне проекта:

```bash
touch .env
```

Откройте файл `.env` и заполните следующие переменные:

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

# Telegram Bot (опционально на этапе установки)
TELEGRAM_BOT_TOKEN=your-telegram-bot-token

# Режим работы
ENVIRONMENT=development
DEBUG=True
```

**Важно:** 
- `SECRET_KEY` должен быть минимум 32 символа. Используйте случайную строку
- `SETTINGS_ENCRYPTION_KEY` должен быть ровно 32 байта для AES-256
- Для production используйте безопасные ключи

### Шаг 3: Сборка и запуск контейнеров

```bash
# Собрать Docker образы
make build

# Запустить контейнеры
make up

# Проверить статус контейнеров
docker-compose ps
```

Ожидаемый вывод должен показывать все 5 сервисов в статусе "Up":
- postgres
- redis
- backend
- celery_worker
- celery_beat

### Шаг 4: Инициализация базы данных

```bash
# Применить миграции
make init
```

Эта команда выполнит:
- Применение всех миграций Alembic
- Создание таблиц в базе данных
- Установку начальных данных (если есть)

### Шаг 5: Проверка работы

```bash
# Проверить health check
curl http://localhost:8000/health

# Должен вернуть: {"status":"ok"}
```

## Локальная установка

Если вы хотите запустить проект без Docker:

### Шаг 1: Установка зависимостей

```bash
# Создать виртуальное окружение
python3.13 -m venv venv

# Активировать виртуальное окружение
source venv/bin/activate  # Linux/macOS
# или
venv\Scripts\activate  # Windows

# Установить зависимости
pip install -r requirements.txt
```

### Шаг 2: Установка PostgreSQL и Redis

Установите PostgreSQL 18 и Redis локально:

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install postgresql-18 redis-server
```

**macOS:**
```bash
brew install postgresql@18 redis
```

**Windows:**
- Скачайте PostgreSQL: https://www.postgresql.org/download/windows/
- Скачайте Redis: https://github.com/microsoftarchive/redis/releases

### Шаг 3: Настройка локальной базы данных

```bash
# Создать базу данных
sudo -u postgres psql
CREATE DATABASE mgc_audits;
CREATE USER mgc_audits WITH PASSWORD 'mgc_audits_password';
GRANT ALL PRIVILEGES ON DATABASE mgc_audits TO mgc_audits;
\q
```

### Шаг 4: Настройка .env для локальной установки

Отредактируйте `.env` для подключения к локальной БД:

```env
DATABASE_URL=postgresql+asyncpg://mgc_audits:mgc_audits_password@localhost:5432/mgc_audits
REDIS_URL=redis://localhost:6379/0
```

### Шаг 5: Запуск миграций

```bash
# Применить миграции
alembic upgrade head
```

### Шаг 6: Запуск сервисов

В отдельных терминалах:

```bash
# Терминал 1: Backend сервер
uvicorn app.main:app --reload

# Терминал 2: Celery worker
celery -A app.core.celery_worker worker --loglevel=info

# Терминал 3: Celery beat
celery -A app.core.celery_worker beat --loglevel=info
```

## Настройка базы данных

### Создание резервной копии

```bash
# Создать бэкап
docker-compose exec postgres pg_dump -U mgc_audits mgc_audits > backup.sql

# Восстановить из бэкапа
docker-compose exec -T postgres psql -U mgc_audits mgc_audits < backup.sql
```

### Работа с миграциями

```bash
# Создать новую миграцию
make migrate msg="описание изменений"

# Применить миграции
make upgrade

# Откатить последнюю миграцию
docker-compose exec backend alembic downgrade -1

# Просмотреть историю миграций
docker-compose exec backend alembic history
```

## Настройка интеграций

Интеграции настраиваются через веб-интерфейс администратора после установки.

### S3 Storage (Yandex Object Storage)

1. Получите credentials от Yandex Cloud
2. Перейдите в админку: Настройки → Интеграции → S3 Storages
3. Создайте новое подключение:
   - Endpoint URL: `https://storage.yandexcloud.net`
   - Region: `ru-central1`
   - Access Key ID: ваш ключ
   - Secret Access Key: ваш секретный ключ
   - Bucket name: имя bucket

### SMTP (Email)

1. Получите учетные данные SMTP от Yandex Mail
2. Перейдите в админку: Настройки → Интеграции → Email Accounts
3. Создайте новый аккаунт:
   - SMTP Host: `smtp.yandex.ru`
   - SMTP Port: `587`
   - Username: ваш email
   - Password: пароль приложения
   - Use TLS: True

### LDAP

1. Получите данные от IT отдела для подключения к AD
2. Перейдите в админку: Настройки → Интеграции → LDAP Connections
3. Создайте новое подключение:
   - Server URI: `ldap://your.domain.com`
   - Bind DN: CN=Admin,CN=Users,DC=domain,DC=com
   - Bind Password: пароль
   - User Search Base: `ou=users,dc=domain,dc=com`

### Telegram Bot

1. Создайте бота через @BotFather в Telegram
2. Получите токен бота
3. Добавьте токен в `.env`:
   ```env
   TELEGRAM_BOT_TOKEN=your-bot-token
   ```
4. Перезапустите контейнеры:
   ```bash
   make restart
   ```

## Проверка установки

### Проверка статуса сервисов

```bash
# Статус всех контейнеров
docker-compose ps

# Логи backend
docker-compose logs backend

# Логи PostgreSQL
docker-compose logs postgres

# Логи Celery
docker-compose logs celery_worker
```

### Проверка API

```bash
# Health check
curl http://localhost:8000/health

# Swagger документация
open http://localhost:8000/docs
```

### Тестовый запрос

```bash
# Регистрация нового пользователя
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123456",
    "first_name_ru": "Тест",
    "last_name_ru": "Тестов"
  }'
```

## Устранение неполадок

### Проблема: Контейнеры не запускаются

**Решение:**
```bash
# Проверить логи
make logs

# Пересобрать образы
make clean
make build
make up
```

### Проблема: Ошибка подключения к БД

**Решение:**
```bash
# Проверить что PostgreSQL запущен
docker-compose ps postgres

# Проверить логи PostgreSQL
docker-compose logs postgres

# Пересоздать БД
docker-compose down -v
make up
make init
```

### Проблема: Ошибки миграций

**Решение:**
```bash
# Просмотреть историю миграций
docker-compose exec backend alembic history

# Откатить к предыдущей версии
docker-compose exec backend alembic downgrade -1

# Повторно применить миграции
make upgrade
```

### Проблема: Celery задачи не выполняются

**Решение:**
```bash
# Проверить что Redis запущен
docker-compose ps redis

# Проверить логи Celery worker
docker-compose logs celery_worker

# Перезапустить Celery
docker-compose restart celery_worker celery_beat
```

### Проблема: Порты заняты

**Решение:**

Измените порты в `docker-compose.yml`:

```yaml
ports:
  - "8001:8000"  # Изменить 8000 на 8001
```

Или остановите конкурирующие сервисы.

## Дополнительная помощь

- **API документация:** http://localhost:8000/docs
- **README:** см. файл README.md
- **Архитектура:** см. файл PROJECT_DESIGN.md в `/docs`

Если проблема не решена, обратитесь к администратору системы.

