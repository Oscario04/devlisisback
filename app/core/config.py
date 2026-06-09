from functools import lru_cache
from urllib.parse import urlparse

from dotenv import load_dotenv
from pydantic import AliasChoices
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    project_name: str = Field(default="Devlisis API", alias="PROJECT_NAME")
    service_name: str = Field(default="devlisis-api", alias="SERVICE_NAME")
    api_v1_prefix: str = Field(default="/api", alias="API_V1_PREFIX")

    mongodb_uri: str = Field(
        ...,
        alias="MONGODB_URI",
        validation_alias=AliasChoices("MONGODB_URI", "MONGODB_URL"),
    )
    mongodb_db_name: str = Field(default="devlisis", alias="MONGODB_DB_NAME")

    smtp_host: str | None = Field(default=None, alias="SMTP_HOST")
    smtp_port: int | None = Field(default=None, alias="SMTP_PORT")
    smtp_user: str | None = Field(default=None, alias="SMTP_USER")
    smtp_password: str | None = Field(default=None, alias="SMTP_PASSWORD")
    smtp_from: str | None = Field(default=None, alias="SMTP_FROM")
    smtp_use_tls: bool = Field(default=True, alias="SMTP_USE_TLS")
    smtp_timeout_seconds: int = Field(default=15, alias="SMTP_TIMEOUT_SECONDS", ge=3, le=120)

    turnstile_secret_key: str | None = Field(default=None, alias="TURNSTILE_SECRET_KEY")
    turnstile_enabled: bool = Field(default=True, alias="TURNSTILE_ENABLED")
    turnstile_timeout_seconds: int = Field(default=5, alias="TURNSTILE_TIMEOUT_SECONDS", ge=2, le=30)

    frontend_url: str = Field(default="http://localhost:5173", alias="FRONTEND_URL")
    cors_allow_credentials: bool = Field(default=True, alias="CORS_ALLOW_CREDENTIALS")
    enable_docs: bool = Field(default=True, alias="ENABLE_DOCS")
    contact_dedupe_window_seconds: int = Field(
        default=120,
        alias="CONTACT_DEDUPE_WINDOW_SECONDS",
        ge=30,
        le=900,
    )
    contact_rate_limit_requests: int = Field(default=5, alias="CONTACT_RATE_LIMIT_REQUESTS", ge=1, le=100)
    contact_rate_limit_window_seconds: int = Field(
        default=600,
        alias="CONTACT_RATE_LIMIT_WINDOW_SECONDS",
        ge=60,
        le=3600,
    )
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    def cors_origins(self) -> list[str]:
        values = [origin.strip() for origin in self.frontend_url.split(",") if origin.strip()]
        valid_values: list[str] = []
        for origin in values:
            if origin == "*":
                valid_values.append(origin)
                continue
            parsed = urlparse(origin)
            if parsed.scheme in {"http", "https"} and parsed.netloc:
                valid_values.append(origin)

        values = valid_values
        return values or ["http://localhost:5173"]

    def safe_cors_allow_credentials(self) -> bool:
        origins = self.cors_origins()
        if "*" in origins:
            return False
        return self.cors_allow_credentials

    def smtp_is_configured(self) -> bool:
        return bool(
            self.smtp_host
            and self.smtp_port
            and self.smtp_user
            and self.smtp_password
            and self.smtp_from
        )

    def turnstile_is_configured(self) -> bool:
        return bool(self.turnstile_secret_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
