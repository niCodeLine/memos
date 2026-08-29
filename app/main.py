from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.db.schema import ensure_schema
from app.routers import admin, ai, health, reminders


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_schema()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="Self-hosted reminder platform for assistants, bots and local automations.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(health.router)
app.include_router(admin.router)
app.include_router(ai.router)
app.include_router(reminders.router)
