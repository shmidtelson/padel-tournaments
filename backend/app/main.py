"""FastAPI application entry point. DDD: infrastructure API layer."""

import logging
import uuid

import sentry_sdk
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.responses import HTMLResponse
from sentry_sdk.integrations.fastapi import FastApiIntegration
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.infrastructure.api.routes import (
    admin,
    auth,
    billing,
    blog,
    contact,
    organizations,
    tournaments,
)

logging.basicConfig(level=logging.INFO if not settings.debug else logging.DEBUG)
logger = logging.getLogger(__name__)

if not settings.debug:
    try:
        settings.validate_production()
    except ValueError as e:
        logger.critical("Startup aborted: %s", e)
        raise

if settings.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.sentry_environment,
        traces_sample_rate=settings.sentry_traces_sample_rate,
        integrations=[FastApiIntegration()],
        send_default_pii=False,
    )

app = FastAPI(
    title=settings.app_name,
    description="API для платформы турниров по паделу: организации, турниры, раунды, матчи, биллинг (Stripe), админка и блог.",
    version="0.1.0",
    docs_url=None,  # отдаём через кастомные роуты с проверкой ключа
    redoc_url=None,
    openapi_url=None,
)


def _docs_key_ok(request: Request, docs_key: str | None = Query(None, alias="docs_key")) -> bool:
    if not settings.docs_secret_key:
        return True
    key = docs_key or request.headers.get("X-Docs-Key")
    return key == settings.docs_secret_key


@app.get("/docs", response_class=HTMLResponse, include_in_schema=False)
async def swagger_ui(
    request: Request,
    docs_key: str | None = Query(None, alias="docs_key"),
):
    """Swagger UI. Доступ: ?docs_key=SECRET или заголовок X-Docs-Key (если в .env задан DOCS_SECRET_KEY)."""
    if not _docs_key_ok(request, docs_key):
        raise HTTPException(status_code=403, detail="Invalid or missing docs key")
    q = f"?docs_key={docs_key}" if docs_key else ""
    return get_swagger_ui_html(
        openapi_url=f"/openapi.json{q}",
        title=app.title + " — Swagger",
    )


@app.get("/redoc", response_class=HTMLResponse, include_in_schema=False)
async def redoc_ui(
    request: Request,
    docs_key: str | None = Query(None, alias="docs_key"),
):
    """ReDoc. Доступ: ?docs_key=SECRET или X-Docs-Key (если задан DOCS_SECRET_KEY)."""
    if not _docs_key_ok(request, docs_key):
        raise HTTPException(status_code=403, detail="Invalid or missing docs key")
    q = f"?docs_key={docs_key}" if docs_key else ""
    return get_redoc_html(
        openapi_url=f"/openapi.json{q}",
        title=app.title + " — ReDoc",
    )


@app.get("/openapi.json", include_in_schema=False)
async def openapi_json(
    request: Request,
    docs_key: str | None = Query(None, alias="docs_key"),
):
    """OpenAPI 3.0 schema. Доступ: ?docs_key=SECRET или X-Docs-Key (если задан DOCS_SECRET_KEY)."""
    if not _docs_key_ok(request, docs_key):
        raise HTTPException(status_code=403, detail="Invalid or missing docs key")
    return app.openapi()


class RequestIdAndLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id
        logger.info(
            "request_start path=%s method=%s request_id=%s",
            request.url.path,
            request.method,
            request_id,
        )
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        logger.info(
            "request_end path=%s status=%s request_id=%s",
            request.url.path,
            response.status_code,
            request_id,
        )
        return response


# CORS: in debug allow *; in production use CORS_ORIGINS
_origins = settings.cors_origins_list() if settings.cors_origins_list() else ["*"]
app.add_middleware(RequestIdAndLogMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(organizations.router)
app.include_router(tournaments.router)
app.include_router(admin.router)
app.include_router(blog.router)
app.include_router(billing.router)
app.include_router(contact.router)


@app.get("/health")
async def health():
    """Liveness: always 200. For readiness (DB) use /health/ready."""
    return {"status": "ok"}


@app.get("/health/ready")
async def health_ready():
    """Readiness: 200 if DB is reachable, else 503."""
    from sqlalchemy import text

    from app.core.database import AsyncSessionLocal

    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        return {"status": "ok", "db": "up"}
    except Exception as e:
        logger.warning("health_ready failed: %s", e)
        raise HTTPException(status_code=503, detail="Database unavailable") from e
