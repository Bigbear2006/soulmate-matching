args = bot

all: up

env:
	@if [ ! -f .env ]; then \
        echo "Creating .env from .env.example"; \
        cat .env.example >> .env; \
    else \
        echo ".env already exists."; \
    fi

up:
	docker-compose up --build -d

down:
	docker-compose down

restart:
	docker-compose restart $(args)

stop:
	docker-compose stop $(args)

rebuild:
	docker-compose up --build -d --no-deps $(args)

logs:
	docker-compose logs -f $(args)

migrations:
	docker-compose exec django python manage.py makemigrations

migrate:
	docker-compose exec django python manage.py migrate

admin:
	docker-compose exec django python manage.py createsuperuser

shell:
	docker-compose exec django python manage.py shell

lint:
	ruff format
	ruff check --fix
	ruff format

dev: lint restart logs
