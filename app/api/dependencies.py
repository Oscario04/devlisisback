from fastapi import Depends, HTTPException, Request
from starlette import status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.rate_limit import InMemoryRateLimiter
from app.database.session import get_db
from app.repositories.contact_repository import ContactRequestRepository
from app.services.contact_service import ContactService
from app.services.email_service import SmtpEmailService
from app.services.turnstile_service import CloudflareTurnstileService, TurnstileService

contact_rate_limiter = InMemoryRateLimiter(
    max_requests=settings.contact_rate_limit_requests,
    window_seconds=settings.contact_rate_limit_window_seconds,
)


def get_contact_service(db: Session = Depends(get_db)) -> ContactService:
    repository = ContactRequestRepository(db=db)
    email_service = SmtpEmailService()
    return ContactService(repository=repository, email_service=email_service)


def get_turnstile_service() -> TurnstileService:
    return CloudflareTurnstileService()


def get_client_ip(request: Request) -> str:
    cf_ip = request.headers.get("CF-Connecting-IP")
    if cf_ip:
        return cf_ip

    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    if request.client and request.client.host:
        return request.client.host

    return "unknown"


def enforce_contact_rate_limit(client_ip: str = Depends(get_client_ip)) -> None:
    if not contact_rate_limiter.is_allowed(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests.",
        )
