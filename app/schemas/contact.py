from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class ContactRequestCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Nombre del contacto")
    company: str | None = Field(default=None, max_length=150, description="Empresa")
    email: EmailStr = Field(..., max_length=254, description="Correo electrónico")
    phone: str | None = Field(default=None, max_length=30, description="Teléfono")
    message: str = Field(..., min_length=20, max_length=3000, description="Mensaje del lead")
    turnstile_token: str | None = Field(default=None, min_length=1, description="Token de Cloudflare Turnstile")

    @field_validator("name", "company", "phone", "message", "turnstile_token", mode="before")
    @classmethod
    def normalize_text_fields(cls, value: str | None) -> str | None:
        if value is None:
            return None
        sanitized = " ".join(value.replace("\x00", "").split())
        return sanitized.strip()


class ContactRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    company: str | None
    email: EmailStr
    phone: str | None
    message: str
    created_at: datetime


class ContactRequestListResponse(BaseModel):
    items: list[ContactRequestResponse]
