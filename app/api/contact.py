from fastapi import APIRouter, Depends, status
from fastapi import HTTPException
from starlette import status as http_status

from app.api.dependencies import (
    enforce_contact_rate_limit,
    get_client_ip,
    get_contact_service,
    get_turnstile_service,
)
from app.schemas.contact import (
    ContactRequestCreate,
    ContactRequestListResponse,
    ContactRequestResponse,
)
from app.services.contact_service import ContactService
from app.services.turnstile_service import TurnstileService

router = APIRouter(prefix="/api/contact", tags=["contact"])


@router.post(
    "",
    response_model=ContactRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create contact request",
)
def create_contact_request(
    payload: ContactRequestCreate,
    _: None = Depends(enforce_contact_rate_limit),
    client_ip: str = Depends(get_client_ip),
    turnstile_service: TurnstileService = Depends(get_turnstile_service),
    service: ContactService = Depends(get_contact_service),
) -> ContactRequestResponse:
    if not turnstile_service.validate_token(payload.turnstile_token, remote_ip=client_ip):
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Invalid Turnstile token.",
        )

    contact = service.create_contact_request(payload)
    return ContactRequestResponse.model_validate(contact)


@router.get(
    "",
    response_model=ContactRequestListResponse,
    summary="List contact requests",
)
def list_contact_requests(
    service: ContactService = Depends(get_contact_service),
) -> ContactRequestListResponse:
    # TODO: Este endpoint será protegido con JWT en la siguiente fase.
    items = service.list_contact_requests()
    return ContactRequestListResponse(items=[ContactRequestResponse.model_validate(item) for item in items])
