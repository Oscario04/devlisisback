import logging

from fastapi import FastAPI, Request
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette import status

logger = logging.getLogger(__name__)


class EmailDeliveryError(Exception):
    def __init__(self, message: str = "No se pudo enviar el correo del lead") -> None:
        self.message = message
        super().__init__(self.message)


def _request_id_header(request: Request) -> dict[str, str]:
    request_id = getattr(request.state, "request_id", None)
    if request_id:
        return {"X-Request-ID": request_id}
    return {}


def _sanitize_validation_errors(exc: RequestValidationError) -> list[dict[str, str | list[str]]]:
    sanitized: list[dict[str, str | list[str]]] = []
    for err in exc.errors():
        loc = [str(item) for item in err.get("loc", [])]
        sanitized.append(
            {
                "loc": loc,
                "msg": str(err.get("msg", "Validation error")),
                "type": str(err.get("type", "value_error")),
            }
        )
    return sanitized


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        logger.warning("Validation error", extra={"errors": exc.errors()})
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": "Error de validación en la solicitud.",
                "errors": _sanitize_validation_errors(exc),
            },
            headers=_request_id_header(request),
        )

    @app.exception_handler(EmailDeliveryError)
    async def email_delivery_exception_handler(request: Request, exc: EmailDeliveryError) -> JSONResponse:
        logger.error("Email delivery failed", extra={"error": exc.message})
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={"detail": exc.message},
            headers=_request_id_header(request),
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        logger.warning("HTTP exception", extra={"status_code": exc.status_code, "detail": str(exc.detail)})
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": str(exc.detail)},
            headers=_request_id_header(request),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled exception", exc_info=exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Error interno del servidor."},
            headers=_request_id_header(request),
        )
