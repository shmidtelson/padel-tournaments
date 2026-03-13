"""Очереди Procrastinate (PostgreSQL). Для локальной разработки: docker compose up -d postgres && procrastinate --app=app.queues:app worker."""

import os

import procrastinate

from app.core.config import settings

# Sync URL для воркера (в Docker можно передать DATABASE_URL=postgresql://...)
_dsn = os.getenv("DATABASE_URL") or settings.database_url_sync
if _dsn.startswith("postgresql+asyncpg://"):
    _dsn = _dsn.replace("postgresql+asyncpg://", "postgresql://", 1)

app = procrastinate.App(connector=procrastinate.PsycopgConnector(dsn=_dsn))


@app.task(queue="default")
def example_task(message: str) -> str:
    """Пример задачи (для проверки очереди)."""
    return f"Processed: {message}"
