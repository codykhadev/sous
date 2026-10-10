# Sous

A recipe web app that turns recipe websites and cooking videos into clean, structured recipes, then walks you through cooking them one step at a time with built-in timers.

Everything runs locally on free, open-source tools. No paid APIs, no API keys, no accounts.

> Work in progress. Currently: project scaffold (FastAPI + Postgres + React).

## Tech stack

**Backend**: Python, FastAPI, SQLAlchemy, Alembic, Postgres
**Frontend**: React, TypeScript, Vite, Tailwind CSS, React Router
**Infrastructure**: Docker, Docker Compose

## Running it

Requires [Docker Desktop](https://www.docker.com/products/docker-desktop/).

```bash
docker compose up -d --build
```

Open `http://localhost:8000`. API docs are at `http://localhost:8000/api/docs`.

Stop with `docker compose down`. Saved data is kept in a Docker volume; `docker compose down -v` deletes it.

## Development

Run Postgres in Docker and the backend and frontend locally with hot reload:

```bash
make db                     # Postgres container

cd backend
python3 -m venv venv
venv/bin/pip install -r requirements-dev.txt
cd ..
make backend                # FastAPI on :8000 (stop the Docker backend first: docker compose stop backend)

cd frontend && npm install && cd ..
make frontend               # Vite on :5173, proxies /api to :8000
```
