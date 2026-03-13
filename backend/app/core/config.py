from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    app_name: str = "Padel Tournaments API"
    debug: bool = False

    # Database (async for FastAPI/SQLAlchemy)
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/padel_tournaments"
    # Sync URL for Procrastinate worker (postgresql://)
    database_url_sync: str = "postgresql://postgres:postgres@localhost:5432/padel_tournaments"
    # Pool (production)
    database_pool_size: int = 5
    database_max_overflow: int = 10

    # JWT. In production set SECRET_KEY (min 32 chars); app refuses to start with default if debug=False
    secret_key: str = "change-me-in-production-use-env"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7

    # SMS (placeholder - set in env for real provider)
    sms_provider_url: str = ""
    sms_api_key: str = ""

    # Telegram bot (for Login Widget verification)
    telegram_bot_token: str = ""

    # Stripe (оплата тарифов для организаций)
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_price_id_pro: str = ""  # Price ID тарифа Pro (рекуррент)

    # Private docs: если задан, /docs и /openapi.json доступны только с ?docs_key=... или заголовком X-Docs-Key
    docs_secret_key: str = ""

    # Sentry (ошибки и трейсы; если пусто — Sentry отключён)
    sentry_dsn: str = ""
    sentry_environment: str = "development"
    sentry_traces_sample_rate: float = 0.1

    # CORS: comma-separated origins, e.g. https://app.example.com,https://www.example.com. If empty and not debug, "*" is not allowed.
    cors_origins: str = ""
    # Allowed base URL for Stripe checkout success_url/cancel_url (e.g. https://app.example.com)
    allowed_frontend_base_url: str = ""

    def cors_origins_list(self) -> list[str]:
        if not self.cors_origins.strip():
            return []
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    def validate_production(self) -> None:
        """Raise if production-insecure config. Call at app startup when debug=False."""
        if self.debug:
            return
        if self.secret_key in ("", "change-me-in-production-use-env") or len(self.secret_key) < 32:
            raise ValueError(
                "SECRET_KEY must be set and at least 32 characters in production. "
                "Set DEBUG=true only for local development."
            )
        if not self.cors_origins_list():
            raise ValueError(
                "CORS_ORIGINS must be set in production (e.g. https://your-frontend.com). "
                "Set DEBUG=true only for local development."
            )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
