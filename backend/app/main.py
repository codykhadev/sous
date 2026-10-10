from fastapi import APIRouter, FastAPI

from .config import settings
from .frontend import mount_frontend
from .routers import health

app = FastAPI(title="Sous", docs_url="/api/docs", openapi_url="/api/openapi.json", redoc_url=None)

api = APIRouter(prefix="/api")
api.include_router(health.router)
app.include_router(api)

if settings.static_dir and settings.static_dir.is_dir():
    mount_frontend(app, settings.static_dir)
