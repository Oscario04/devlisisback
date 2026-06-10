from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging
from app.core.middleware import RequestLogMiddleware
from app.database.session import close_mongo_connection, initialize_mongo_indexes
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 🔥 TODO runtime-safe (NO import-time)
    configure_logging()
    initialize_mongo_indexes()

    yield

    close_mongo_connection()


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.project_name,
        version="1.0.0",
        docs_url="/docs" if settings.enable_docs else None,
        redoc_url="/redoc" if settings.enable_docs else None,
        openapi_url="/openapi.json" if settings.enable_docs else None,
        lifespan=lifespan,
    )

    app.add_middleware(RequestLogMiddleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins(),
        allow_credentials=settings.safe_cors_allow_credentials(),
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)
    app.include_router(api_router)

    return app


# ✅ VERCEL ENTRYPOINT SAFE
app = create_app()