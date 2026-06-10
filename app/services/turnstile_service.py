import json
import logging
from typing import Protocol
from urllib import parse, request
from urllib.error import HTTPError, URLError

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class TurnstileService(Protocol):
    def validate_token(self, token: str | None, remote_ip: str | None = None) -> bool:
        """Validate Cloudflare Turnstile token."""


class CloudflareTurnstileService:
    VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"

    def validate_token(self, token: str | None, remote_ip: str | None = None) -> bool:
        settings = get_settings()  # ✅ runtime safe

        if not settings.turnstile_enabled:
            return True

        if not settings.turnstile_is_configured():
            logger.error("Turnstile validation enabled but secret key missing")
            return False

        if not token:
            return False

        payload = {
            "secret": settings.turnstile_secret_key,
            "response": token,
        }

        if remote_ip:
            payload["remoteip"] = remote_ip

        encoded = parse.urlencode(payload).encode("utf-8")
        req = request.Request(self.VERIFY_URL, data=encoded, method="POST")

        try:
            with request.urlopen(req, timeout=settings.turnstile_timeout_seconds) as response:
                body = response.read().decode("utf-8")
                result = json.loads(body)
                return bool(result.get("success", False))

        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError):
            logger.warning("Turnstile verification failed due to network error")
            return False