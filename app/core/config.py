from functools import lru_cache
from urllib.parse import urlparse

from dotenv import load_dotenv
from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Carga local (en Vercel no afecta, pero útil en dev)
load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ---------------- Core ----------------
    project_name: str = Field(default="Devlisis API", alias="PROJECT_NAME")
    service_name: str = Field(default="devlisis-api", alias="SERVICE_NAME")
    api_v1_prefix: str = Field(default="/api", alias="API_V1_PREFIX")

    # ---------------- MongoDB ----------------
    mongodb_uri: str = Field(
        ...,
        alias="MONGODB_URI",
        validation_alias=AliasChoices("MONGODB_URI", "MONGODB_URL"),
    )
    mongodb_db_name: str = Field(default="devlisis", alias="MONGODB_DB_NAME")

    # ---------------- SMTP ----------------
    smtp_host: str | None = Field(default=None, alias="SMTP_HOST")
    smtp_port: int | None = Field(default=None, alias="SMTP_PORT")
    smtp_user: str | None = Field(default=None, alias="SMTP_USER")
    smtp_password: str | None = Field(default=None, alias="SMTP_PASSWORD")
    smtp_from: str | None = Field(default=None, alias="SMTP_FROM")
    smtp_use_tls: bool = Field(default=True, alias="SMTP_USE_TLS")
    smtp_timeout_seconds: int = Field(default=15, alias="SMTP_TIMEOUT_SECONDS", ge=3, le=120)

    # ---------------- Turnstile ----------------
    turnstile_secret_key: str | None = Field(default=None, alias="TURNSTILE_SECRET_KEY")
    turnstile_enabled: bool = Field(default=True, alias="TURNSTILE_ENABLED")
    turnstile_timeout_seconds: int = Field(default=5, alias="TURNSTILE_TIMEOUT_SECONDS", ge=2, le=30)

    # ---------------- Frontend / CORS ----------------
    frontend_url: str = Field(default="https://devlisis.com", alias="FRONTEND_URL")
    cors_allow_credentials: bool = Field(default=True, alias="CORS_ALLOW_CREDENTIALS")

    # ---------------- App config ----------------
    enable_docs: bool = Field(default=True, alias="ENABLE_DOCS")

    contact_dedupe_window_seconds: int = Field(
        default=120,
        alias="CONTACT_DEDUPE_WINDOW_SECONDS",
        ge=30,
        le=900,
    )

    contact_rate_limit_requests: int = Field(
        default=5,
        alias="CONTACT_RATE_LIMIT_REQUESTS",
        ge=1,
        le=100,
    )

    contact_rate_limit_window_seconds: int = Field(
        default=600,
        alias="CONTACT_RATE_LIMIT_WINDOW_SECONDS",
        ge=60,
        le=3600,
    )

    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # ---------------- Helpers ----------------
    def cors_origins(self) -> list[str]:
        values = [o.strip() for o in self.frontend_url.split(",") if o.strip()]
        valid: list[str] = []

        for origin in values:
            if origin == "*":
                valid.append(origin)
                continue

            parsed = urlparse(origin)
            if parsed.scheme in {"http", "https"} and parsed.netloc:
                valid.append(origin)

        return valid or ["http://localhost:5173"]

    def safe_cors_allow_credentials(self) -> bool:
        return self.cors_allow_credentials and "*" not in self.cors_origins()

    def smtp_is_configured(self) -> bool:
        return all(
            [
                self.smtp_host,
                self.smtp_port,
                self.smtp_user,
                self.smtp_password,
                self.smtp_from,
            ]
        )

    def turnstile_is_configured(self) -> bool:
        return bool(self.turnstile_secret_key)


# ---------------- SAFE SINGLETON ----------------
@lru_cache
def get_settings() -> Settings:
    """
    Safe for Vercel / FastAPI:
    - avoids import-time crashes
    - lazy initialization
    - cached instance
    """
    return Settings()