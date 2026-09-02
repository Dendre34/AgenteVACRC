import logging
import secrets

from fastapi import Request, Security
from fastapi.security import APIKeyHeader

from app.core.config import settings
from app.core.errors import TokenError

logger = logging.getLogger(__name__)

api_key_header = APIKeyHeader(name="X-API-Token", auto_error=False)


def verify_api_token(request: Request, api_token: str | None = Security(api_key_header)) -> None:
    if not api_token or not secrets.compare_digest(api_token, settings.API_TOKEN):
        client_host = request.client.host if request.client else "desconocido"
        logger.warning("Intento de acceso con token inválido o ausente desde %s", client_host)
        raise TokenError(msg="Token de autenticación inválido o ausente.")
