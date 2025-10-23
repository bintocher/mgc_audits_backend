# Инструкция по развертыванию MGC Audits Backend на Production

## Содержание

1. [Подготовка сервера](#подготовка-сервера)
2. [Настройка окружения](#настройка-окружения)
3. [Развертывание приложения](#развертывание-приложения)
4. [Настройка Nginx](#настройка-nginx)
5. [Настройка SSL](#настройка-ssl)
6. [Настройка бэкапов](#настройка-бэкапов)
7. [Мониторинг и логирование](#мониторинг-и-логирование)
8. [Масштабирование](#масштабирование)
9. [Обновление приложения](#обновление-приложения)

## Подготовка сервера

### Требования к серверу

- **ОС:** Ubuntu 22.04 LTS или Ubuntu 24.04 LTS
- **CPU:** 4+ ядра
- **RAM:** 8+ GB
- **Диск:** 50+ GB SSD
- **Сеть:** Статический IP адрес

### Установка Docker

```bash
# Обновить пакеты
sudo apt-get update

# Установить необходимые пакеты
sudo apt-get install apt-transport-https ca-certificates curl gnupg lsb-release

# Добавить официальный GPG ключ Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Добавить репозиторий Docker
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Установить Docker
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Добавить пользователя в группу docker
sudo usermod -aG docker $USER

# Проверить установку
docker --version
docker compose version
```

### Установка Nginx

```bash
sudo apt-get install nginx

# Проверить статус
sudo systemctl status nginx
```

### Базовое обеспечение безопасности

```bash
# Настроить firewall
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# Установить fail2ban
sudo apt-get install fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

## Настройка окружения

### Создание пользователя для приложения

```bash
# Создать пользователя
sudo adduser mgc-audits --disabled-password --gecos ""

# Добавить в группу docker
sudo usermod -aG docker mgc-audits

# Переключиться на пользователя
sudo su - mgc-audits
```

### Структура директорий

```bash
# Создать директории
mkdir -p /home/mgc-audits/app
mkdir -p /home/mgc-audits/backups
mkdir -p /home/mgc-audits/logs
```

### Клонирование репозитория

```bash
cd /home/mgc-audits/app
git clone <repository-url> backend
cd backend
```

### Настройка .env для Production

Создайте файл `.env` с production настройками:

```env
# База данных PostgreSQL
DATABASE_URL=postgresql+asyncpg://mgc_audits:STRONG_PASSWORD_HERE@postgres:5432/mgc_audits

# Redis
REDIS_URL=redis://redis:6379/0

# Безопасность - ОБЯЗАТЕЛЬНО ИЗМЕНИТЕ!
SECRET_KEY=GENERATE_STRONG_SECRET_KEY_MIN_32_CHARS_HERE
SETTINGS_ENCRYPTION_KEY=GENERATE_32_BYTE_KEY_HERE!!

# JWT
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Telegram Bot
TELEGRAM_BOT_TOKEN=your-telegram-bot-token

# Production настройки
ENVIRONMENT=production
DEBUG=False

# Логирование
LOG_LEVEL=INFO
```

**Важно:** Используйте генератор для создания безопасных ключей:

```bash
# Генерация SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Генерация SETTINGS_ENCRYPTION_KEY (32 байта)
python3 -c "import secrets; print(secrets.token_urlsafe(24)[:32])"
```

## Развертывание приложения

### Сборка и запуск

```bash
cd /home/mgc-audits/app/backend

# Собрать образы
docker compose build

# Запустить контейнеры
docker compose up -d

# Проверить статус
docker compose ps

# Проверить логи
docker compose logs -f
```

### Инициализация базы данных

```bash
# Применить миграции
docker compose exec backend alembic upgrade head

# Проверить миграции
docker compose exec backend alembic current
```

### Настройка автоматического запуска

Создайте systemd service для автоматического запуска контейнеров:

```bash
sudo nano /etc/systemd/system/mgc-audits.service
```

Содержимое файла:

```ini
[Unit]
Description=MGC Audits Backend
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/mgc-audits/app/backend
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down
User=mgc-audits
Group=mgc-audits

[Install]
WantedBy=multi-user.target
```

Активировать service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable mgc-audits
sudo systemctl start mgc-audits
```

## Настройка Nginx

### Создание конфигурации

```bash
sudo nano /etc/nginx/sites-available/mgc-audits-api
```

Содержимое файла:

```nginx
upstream backend_app {
    server localhost:8000;
}

server {
    listen 80;
    server_name api.example.com;

    # Логи
    access_log /var/log/nginx/mgc-audits-api-access.log;
    error_log /var/log/nginx/mgc-audits-api-error.log;

    # Ограничения
    client_max_body_size 100M;
    proxy_read_timeout 300s;
    proxy_connect_timeout 300s;

    location / {
        proxy_pass http://backend_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://backend_app/health;
        access_log off;
    }
}
```

Активировать конфигурацию:

```bash
sudo ln -s /etc/nginx/sites-available/mgc-audits-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Настройка SSL

### Установка Certbot

```bash
sudo apt-get install certbot python3-certbot-nginx
```

### Получение SSL сертификата

```bash
sudo certbot --nginx -d api.example.com
```

Certbot автоматически настроит Nginx и обновит конфигурацию.

### Автоматическое обновление сертификата

```bash
# Проверить автопродление
sudo certbot renew --dry-run

# Certbot автоматически добавляет cron задачу
sudo crontab -l | grep certbot
```

## Настройка бэкапов

### Скрипт бэкапа базы данных

Создайте скрипт `/home/mgc-audits/backups/backup-db.sh`:

```bash
#!/bin/bash

BACKUP_DIR="/home/mgc-audits/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/mgc_audits_$DATE.sql"

# Создать бэкап
docker compose exec -T postgres pg_dump -U mgc_audits mgc_audits > "$BACKUP_FILE"

# Сжать бэкап
gzip "$BACKUP_FILE"

# Удалить старые бэкапы (старше 30 дней)
find "$BACKUP_DIR" -name "mgc_audits_*.sql.gz" -mtime +30 -delete

echo "Backup created: $BACKUP_FILE.gz"
```

Сделать скрипт исполняемым:

```bash
chmod +x /home/mgc-audits/backups/backup-db.sh
```

### Настройка cron для автоматических бэкапов

```bash
crontab -e
```

Добавить строку:

```cron
# Ежедневный бэкап в 2:00 AM
0 2 * * * /home/mgc-audits/backups/backup-db.sh >> /home/mgc-audits/logs/backup.log 2>&1
```

### Бэкап файлов (если нужен)

Если используются локальные файлы:

```bash
#!/bin/bash

BACKUP_DIR="/home/mgc-audits/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/files_$DATE.tar.gz"

tar -czf "$BACKUP_FILE" /path/to/files

# Удалить старые бэкапы (старше 30 дней)
find "$BACKUP_DIR" -name "files_*.tar.gz" -mtime +30 -delete
```

## Мониторинг и логирование

### Настройка логирования

Настройте ротацию логов в `/etc/logrotate.d/mgc-audits`:

```
/home/mgc-audits/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    missingok
    create 0644 mgc-audits mgc-audits
}
```

### Мониторинг ресурсов

Установите инструменты мониторинга:

```bash
# htop для мониторинга CPU/RAM
sudo apt-get install htop

# iotop для мониторинга диска
sudo apt-get install iotop
```

### Проверка статуса контейнеров

Создайте скрипт для мониторинга `/home/mgc-audits/check-status.sh`:

```bash
#!/bin/bash

echo "=== Docker Containers ==="
docker compose ps

echo ""
echo "=== Disk Usage ==="
df -h

echo ""
echo "=== Memory Usage ==="
free -h

echo ""
echo "=== Last 50 log lines ==="
docker compose logs --tail=50
```

### Настройка алертов

Настройте отправку алертов при проблемах:

```bash
# Установить email утилиту
sudo apt-get install mailutils

# Создать скрипт проверки
nano /home/mgc-audits/check-health.sh
```

Содержимое:

```bash
#!/bin/bash

if ! docker compose ps | grep -q "Up"; then
    echo "WARNING: Some containers are down!" | mail -s "MGC Audits Alert" admin@example.com
fi
```

## Масштабирование

### Увеличение количества Celery workers

Отредактируйте `docker-compose.yml`:

```yaml
celery_worker_1:
  # ... конфигурация

celery_worker_2:
  # ... аналогичная конфигурация

celery_worker_3:
  # ... аналогичная конфигурация
```

### Оптимизация PostgreSQL

Отредактируйте `docker-compose.yml` для PostgreSQL:

```yaml
postgres:
  command: >
    postgres
    -c shared_buffers=256MB
    -c effective_cache_size=1GB
    -c maintenance_work_mem=128MB
    -c checkpoint_completion_target=0.9
    -c wal_buffers=16MB
    -c default_statistics_target=100
    -c random_page_cost=1.1
    -c effective_io_concurrency=200
```

### Настройка Redis для высокой доступности

Для production рекомендуется использовать Redis Sentinel или Redis Cluster.

## Обновление приложения

### Процесс обновления

```bash
cd /home/mgc-audits/app/backend

# 1. Создать бэкап БД
/home/mgc-audits/backups/backup-db.sh

# 2. Получить последние изменения
git pull origin main

# 3. Пересобрать образы
docker compose build

# 4. Остановить приложение
docker compose down

# 5. Запустить с новыми образами
docker compose up -d

# 6. Применить миграции
docker compose exec backend alembic upgrade head

# 7. Проверить логи
docker compose logs -f
```

### Rollback при проблемах

```bash
# Откатить на предыдущую версию
git checkout <previous-commit>

# Пересобрать и запустить
docker compose build
docker compose up -d

# Восстановить бэкап БД если нужно
docker compose exec -T postgres psql -U mgc_audits mgc_audits < /home/mgc-audits/backups/mgc_audits_YYYYMMDD.sql
```

## Производительность

### Оптимизация для production

1. **Отключить debug mode:**
   ```env
   DEBUG=False
   ```

2. **Настроить партиционирование БД** (см. документацию)

3. **Кеширование:** Используйте Redis для кеширования

4. **CDN:** Настройте CDN для статических файлов

5. **Load Balancing:** Используйте несколько backend инстансов с Nginx

## Проверка работоспособности

После развертывания проверьте:

```bash
# Health check
curl https://api.example.com/health

# API документация
curl https://api.example.com/docs

# Проверка БД
docker compose exec postgres psql -U mgc_audits -c "SELECT COUNT(*) FROM users;"

# Проверка Celery
docker compose logs celery_worker | tail -n 20
```

## Поддержка

При возникновении проблем:

1. Проверьте логи: `docker compose logs`
2. Проверьте статус: `docker compose ps`
3. Проверьте системные ресурсы: `htop`
4. Обратитесь к документации: `/docs`
5. Свяжитесь с администратором системы

