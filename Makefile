.PHONY: help build up down restart logs clean install install-dev init-dev migrate upgrade shell test lint format

help:
	@echo "Доступные команды:"
	@echo "  make build          - Собрать Docker образы"
	@echo "  make up              - Запустить контейнеры"
	@echo "  make down            - Остановить контейнеры"
	@echo "  make restart         - Перезапустить контейнеры"
	@echo "  make logs            - Показать логи"
	@echo "  make clean           - Очистить контейнеры и volumes"
	@echo "  make install         - Установить зависимости"
	@echo "  make install-dev     - Установить зависимости для разработки"
	@echo "  make init-dev        - Инициализировать проект для разработки"
	@echo "  make migrate         - Создать миграцию"
	@echo "  make upgrade         - Применить миграции"
	@echo "  make shell           - Войти в shell контейнера backend"
	@echo "  make test            - Запустить тесты"
	@echo "  make lint            - Проверить код линтером"
	@echo "  make format          - Форматировать код"

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

clean:
	docker-compose down -v
	docker-compose rm -f

install:
	docker-compose exec backend uv pip install -r requirements.txt

install-dev:
	docker-compose exec backend uv pip install -r requirements-dev.txt

init-dev:
	docker-compose exec backend uv pip install -r requirements.txt
	docker-compose exec backend uv pip install -r requirements-dev.txt
	cp .env.example .env 2>/dev/null || true
	docker-compose exec backend alembic upgrade head

migrate:
	docker-compose exec backend alembic revision --autogenerate -m "$(msg)"

upgrade:
	docker-compose exec backend alembic upgrade head

shell:
	docker-compose exec backend /bin/bash

test:
	docker-compose exec backend pytest

lint:
	docker-compose exec backend ruff check .
	docker-compose exec backend mypy .

format:
	docker-compose exec backend black .
	docker-compose exec backend ruff check --fix .
