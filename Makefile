.PHONY: up down logs db backend frontend test migration

up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f backend

db:
	docker compose up -d db

backend:
	cd backend && venv/bin/alembic upgrade head && venv/bin/uvicorn app.main:app --reload --port 8000

frontend:
	cd frontend && npm run dev

test:
	cd backend && venv/bin/pytest -q
	cd frontend && npm run build

migration:
	cd backend && venv/bin/alembic revision --autogenerate -m "$(name)"
