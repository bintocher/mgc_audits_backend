.PHONY: help build up down restart logs clean init migrate upgrade shell

help:
	@echo "Доступные команды:"
	@echo "  make build          - Собрать Docker образы"
	@echo "  make up              - Запустить контейнеры"
	@echo "  make down            - Остановить контейнеры"
	@echo "  make restart         - Перезапустить контейнеры"
	@echo "  make logs            - Показать логи"
	@echo "  make clean           - Очистить контейнеры и volumes"
	@echo "  make init            - Инициализировать проект"
	@echo "  make migrate         - Создать миграцию"
	@echo "  make upgrade         - Применить миграции"
	@echo "  make shell           - Войти в shell контейнера backend"

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

init:
	cp .env.example .env 2>/dev/null || true
	docker-compose exec backend alembic upgrade head

migrate:
	docker-compose exec backend alembic revision --autogenerate -m "$(msg)"

upgrade:
	docker-compose exec backend alembic upgrade head

shell:
	docker-compose exec backend /bin/bash
