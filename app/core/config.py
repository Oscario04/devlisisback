from functools import lru_cache
from urllib.parse import urlparse

from dotenv import load_dotenv
from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    project_name: str = Field(default="Devlisis API", alias="PROJECT_NAME")
    service_name: str = Field(default="devlisis-api", alias="SERVICE_NAME")

    api_v1_prefix: str = Field(default="/api", alias="API_V1_PREFIX")

    # 🔥 REQUIRED ENV VAR
    mongodb_uri: str = Field(
        ...,
        alias="MONGODB_URI",
        validation_alias=AliasChoices("MONGODB_URI", "MONGODB_URL"),
    )

    mongodb_db_name: str = Field(default="devlisis", alias="MONGODB_DB_NAME")

    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    frontend_url: str = Field(default="https://devlisis.com", alias="FRONTEND_URL")

    cors_allow_credentials: bool = Field(default=True, alias="CORS_ALLOW_CREDENTIALS")

    enable_docs: bool = Field(default=True, alias="ENABLE_DOCS")

    def cors_origins(self) -> list[str]:
        values = [o.strip() for o in self.frontend_url.split(",") if o.strip()]
        valid = []

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


# 🔥 SAFE SINGLETON
@lru_cache
def get_settings() -> Settings:
    return Settings()