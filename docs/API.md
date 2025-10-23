# MGC Audits API Документация

## Содержание

1. [Базовый URL](#базовый-url)
2. [Аутентификация](#аутентификация)
3. [Основные группы API](#основные-группы-api)
4. [Примеры запросов](#примеры-запросов)
5. [Коды ошибок](#коды-ошибок)

## Базовый URL

```
http://localhost:8000/api/v1
```

Для production:
```
https://api.example.com/api/v1
```

## Аутентификация

Большинство API endpoints требуют JWT токен в заголовке `Authorization`:

```
Authorization: Bearer <access_token>
```

### Получение токена

#### 1. Вход по email и паролю

```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Ответ:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### 2. Регистрация по приглашению

```bash
POST /api/v1/auth/register?token=<invite_token>
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "first_name_ru": "Иван",
  "last_name_ru": "Петров",
  "patronymic_ru": "Сергеевич",
  "first_name_en": "Ivan",
  "last_name_en": "Petrov"
}
```

#### 3. LDAP авторизация

```bash
POST /api/v1/auth/ldap
Content-Type: application/json

{
  "username": "domain\\username",
  "password": "password"
}
```

#### 4. Обновление токена

```bash
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

## Основные группы API

### Аутентификация

- `POST /api/v1/auth/login` - Вход в систему
- `POST /api/v1/auth/register` - Регистрация по приглашению
- `POST /api/v1/auth/refresh` - Обновление токена
- `POST /api/v1/auth/logout` - Выход из системы
- `POST /api/v1/auth/otp/send` - Отправка OTP
- `POST /api/v1/auth/otp/verify` - Проверка OTP
- `POST /api/v1/auth/ldap` - LDAP авторизация
- `POST /api/v1/auth/telegram/link` - Привязка Telegram
- `POST /api/v1/auth/telegram/unlink` - Отвязка Telegram

### Пользователи

- `GET /api/v1/users` - Список пользователей
- `POST /api/v1/users` - Создать пользователя
- `GET /api/v1/users/me` - Текущий пользователь
- `PATCH /api/v1/users/me` - Обновить профиль
- `GET /api/v1/users/{id}` - Получить пользователя
- `PUT /api/v1/users/{id}` - Обновить пользователя
- `DELETE /api/v1/users/{id}` - Удалить пользователя

### Роли и права

- `GET /api/v1/roles` - Список ролей
- `POST /api/v1/roles` - Создать роль
- `GET /api/v1/roles/{id}` - Получить роль
- `PUT /api/v1/roles/{id}` - Обновить роль
- `DELETE /api/v1/roles/{id}` - Удалить роль

### Предприятия

- `GET /api/v1/enterprises` - Список предприятий
- `POST /api/v1/enterprises` - Создать предприятие
- `GET /api/v1/enterprises/{id}` - Получить предприятие
- `PUT /api/v1/enterprises/{id}` - Обновить предприятие
- `DELETE /api/v1/enterprises/{id}` - Удалить предприятие

### Справочники

- `GET /api/v1/dictionaries/types` - Типы справочников
- `POST /api/v1/dictionaries/types` - Создать тип справочника
- `GET /api/v1/dictionaries` - Элементы справочников
- `POST /api/v1/dictionaries` - Создать элемент
- `GET /api/v1/dictionaries/{id}` - Получить элемент
- `PUT /api/v1/dictionaries/{id}` - Обновить элемент
- `DELETE /api/v1/dictionaries/{id}` - Удалить элемент

### Аудиты

- `GET /api/v1/audits` - Список аудитов
- `POST /api/v1/audits` - Создать аудит
- `GET /api/v1/audits/{id}` - Получить аудит
- `PUT /api/v1/audits/{id}` - Обновить аудит
- `DELETE /api/v1/audits/{id}` - Удалить аудит
- `GET /api/v1/audits/calendar/schedule` - График аудитов
- `GET /api/v1/audits/calendar/by_component` - График по компонентам
- `POST /api/v1/audits/{id}/reschedule` - Перенести аудит
- `GET /api/v1/audits/{id}/reschedule_history` - История переносов
- `GET /api/v1/audits/{id}/history` - История изменений
- `POST /api/v1/audits/{id}/export` - Экспорт аудита

### Несоответствия (Findings)

- `GET /api/v1/findings` - Список несоответствий
- `POST /api/v1/findings` - Создать несоответствие
- `GET /api/v1/findings/{id}` - Получить несоответствие
- `PUT /api/v1/findings/{id}` - Обновить несоответствие
- `DELETE /api/v1/findings/{id}` - Удалить несоответствие
- `GET /api/v1/findings/{id}/history` - История изменений
- `POST /api/v1/findings/{id}/delegate` - Делегировать
- `GET /api/v1/findings/{id}/comments` - Комментарии
- `POST /api/v1/findings/{id}/comments` - Добавить комментарий

### Планы аудитов

- `GET /api/v1/audit_plans` - Список планов
- `POST /api/v1/audit_plans` - Создать план
- `GET /api/v1/audit_plans/{id}` - Получить план
- `PUT /api/v1/audit_plans/{id}` - Обновить план
- `DELETE /api/v1/audit_plans/{id}` - Удалить план
- `POST /api/v1/audit_plans/{id}/approve_by_division` - Утвердить на уровне дивизиона
- `POST /api/v1/audit_plans/{id}/approve_by_uk` - Утвердить на уровне УК
- `POST /api/v1/audit_plans/{id}/reject` - Отклонить план

### Workflow

- `GET /api/v1/workflow/statuses` - Список статусов
- `POST /api/v1/workflow/statuses` - Создать статус
- `GET /api/v1/workflow/transitions` - Список переходов
- `POST /api/v1/workflow/transitions` - Создать переход
- `POST /api/v1/workflow/transitions/validate` - Валидация перехода

### Отчеты

- `GET /api/v1/reports/findings` - Отчет по несоответствиям
- `GET /api/v1/reports/by_processes` - Отчет по процессам
- `GET /api/v1/reports/by_solvers` - Отчет по исполнителям
- `GET /api/v1/reports/{report_type}/export` - Экспорт отчета в Excel

### Дашборд

- `GET /api/v1/dashboard/stats` - Общая статистика
- `GET /api/v1/dashboard/my_tasks` - Мои задачи

### Уведомления

- `GET /api/v1/notifications` - Список уведомлений
- `POST /api/v1/notifications/{id}/read` - Отметить как прочитанное
- `POST /api/v1/notifications/read_all` - Отметить все как прочитанные
- `GET /api/v1/notifications/stats` - Статистика уведомлений

### Настройки

- `GET /api/v1/settings` - Список настроек
- `GET /api/v1/settings/{key}` - Получить настройку
- `PUT /api/v1/settings/{key}` - Обновить настройку

### Интеграции

- `GET /api/v1/integrations/s3_storages` - S3 подключения
- `POST /api/v1/integrations/s3_storages` - Создать S3 подключение
- `POST /api/v1/integrations/s3_storages/{id}/test` - Проверить подключение
- `GET /api/v1/integrations/email_accounts` - Email аккаунты
- `POST /api/v1/integrations/email_accounts` - Создать Email аккаунт
- `POST /api/v1/integrations/email_accounts/{id}/test` - Проверить подключение
- `GET /api/v1/integrations/ldap_connections` - LDAP подключения
- `POST /api/v1/integrations/ldap_connections` - Создать LDAP подключение
- `POST /api/v1/integrations/ldap_connections/{id}/test` - Проверить подключение

### API токены

- `GET /api/v1/api_tokens` - Список токенов
- `POST /api/v1/api_tokens` - Создать токен
- `GET /api/v1/api_tokens/{id}` - Получить токен
- `PUT /api/v1/api_tokens/{id}` - Обновить токен
- `POST /api/v1/api_tokens/{id}/rotate` - Ротация токена
- `DELETE /api/v1/api_tokens/{id}` - Отозвать токен

## Примеры запросов

### Создание аудита

```bash
POST /api/v1/audits
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Аудит продукта HAVAL",
  "audit_number": "AUD-2025-001",
  "subject": "Проверка компонентов продукта",
  "enterprise_id": "123e4567-e89b-12d3-a456-426614174000",
  "audit_type_id": "456e7890-e89b-12d3-a456-426614174001",
  "process_id": "789e0123-e89b-12d3-a456-426614174002",
  "status_id": "012e3456-e89b-12d3-a456-426614174003",
  "auditor_id": "345e6789-e89b-12d3-a456-426614174004",
  "audit_date_from": "2025-01-15",
  "audit_date_to": "2025-01-20",
  "year": 2025,
  "audit_category": "product",
  "audit_result": "green",
  "estimated_hours": 40
}
```

### Создание несоответствия

```bash
POST /api/v1/findings
Authorization: Bearer <token>
Content-Type: application/json

{
  "audit_id": "123e4567-e89b-12d3-a456-426614174000",
  "enterprise_id": "456e7890-e89b-12d3-a456-426614174001",
  "title": "Несоответствие требованиям качества",
  "description": "Описание несоответствия",
  "process_id": "789e0123-e89b-12d3-a456-426614174002",
  "status_id": "012e3456-e89b-12d3-a456-426614174003",
  "finding_type": "CAR1",
  "resolver_id": "345e6789-e89b-12d3-a456-426614174004",
  "deadline": "2025-02-01",
  "why_1": "Причина 1",
  "why_2": "Причина 2",
  "why_3": "Причина 3",
  "immediate_action": "Немедленные действия",
  "root_cause": "Коренная причина",
  "long_term_action": "Долгосрочные действия"
}
```

### Получение графика аудитов

```bash
GET /api/v1/audits/calendar/schedule?date_from=2025-01-01&date_to=2025-12-31&audit_category=lra
Authorization: Bearer <token>
```

### Фильтрация и пагинация

Все GET endpoints поддерживают пагинацию и фильтрацию:

```bash
GET /api/v1/findings?skip=0&limit=20&status_id=XXX&deadline_from=2025-01-01
Authorization: Bearer <token>
```

Параметры:
- `skip` - количество записей для пропуска (по умолчанию 0)
- `limit` - количество записей для возврата (по умолчанию 20, максимум 100)
- Остальные параметры зависят от endpoint

## Коды ошибок

### Успешные ответы

- `200 OK` - Успешный запрос
- `201 Created` - Ресурс создан
- `204 No Content` - Успешное удаление

### Ошибки клиента

- `400 Bad Request` - Неверный формат запроса
- `401 Unauthorized` - Требуется аутентификация
- `403 Forbidden` - Недостаточно прав
- `404 Not Found` - Ресурс не найден
- `422 Unprocessable Entity` - Ошибка валидации

### Ошибки сервера

- `500 Internal Server Error` - Внутренняя ошибка сервера
- `503 Service Unavailable` - Сервис недоступен

### Пример ответа с ошибкой

```json
{
  "detail": "Пользователь не найден"
}
```

или для ошибок валидации:

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## Интерактивная документация

После запуска приложения доступна интерактивная документация:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json

## Rate Limiting

API токены могут иметь ограничения по количеству запросов:

- `rate_limit_per_minute` - запросов в минуту
- `rate_limit_per_hour` - запросов в час

При превышении лимита возвращается ошибка `429 Too Many Requests`.

## Дополнительная информация

Полная спецификация API доступна в файле `/docs/api_endpoints.md`.

Для доступа к защищенным endpoint требуется JWT токен в заголовке `Authorization`.

