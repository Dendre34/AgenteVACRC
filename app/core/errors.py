from typing import Any

from fastapi import HTTPException
from starlette.background import BackgroundTask

from app.core.response_code import StandardResponseCode


class BaseExceptionError(Exception):
    """Clase base para las excepciones de negocio de la aplicación."""

    code: int

    def __init__(
        self, *, msg: str | None = None, data: Any = None, background: BackgroundTask | None = None
    ) -> None:
        self.msg = msg
        self.data = data
        # Tarea en segundo plano a ejecutar junto con la respuesta de error: https://www.starlette.io/background/
        self.background = background
        super().__init__(msg)


class HTTPError(HTTPException):
    """Excepción HTTP genérica, útil cuando se necesitan headers personalizados."""

    def __init__(self, *, code: int, msg: Any = None, headers: dict[str, Any] | None = None) -> None:
        super().__init__(status_code=code, detail=msg, headers=headers)


class CustomError(BaseExceptionError):
    """Excepción de negocio con código y mensaje personalizados."""

    def __init__(
        self, *, code: int, msg: str, data: Any = None, background: BackgroundTask | None = None
    ) -> None:
        self.code = code
        super().__init__(msg=msg, data=data, background=background)


class RequestError(BaseExceptionError):
    """Solicitud incorrecta (400)."""

    code = StandardResponseCode.HTTP_400

    def __init__(
        self, *, msg: str = "Solicitud incorrecta", data: Any = None, background: BackgroundTask | None = None
    ) -> None:
        super().__init__(msg=msg, data=data, background=background)


class TokenError(HTTPError):
    """Token de autenticación inválido, ausente o expirado (401)."""

    code = StandardResponseCode.HTTP_401

    def __init__(self, *, msg: str = "No autenticado", headers: dict[str, Any] | None = None) -> None:
        super().__init__(code=self.code, msg=msg, headers=headers or {"WWW-Authenticate": "Bearer"})


class ForbiddenError(BaseExceptionError):
    """Acceso prohibido (403)."""

    code = StandardResponseCode.HTTP_403

    def __init__(
        self, *, msg: str = "Acceso prohibido", data: Any = None, background: BackgroundTask | None = None
    ) -> None:
        super().__init__(msg=msg, data=data, background=background)


class NotFoundError(BaseExceptionError):
    """Recurso no encontrado (404)."""

    code = StandardResponseCode.HTTP_404

    def __init__(
        self, *, msg: str = "Recurso no encontrado", data: Any = None, background: BackgroundTask | None = None
    ) -> None:
        super().__init__(msg=msg, data=data, background=background)


class ConflictError(BaseExceptionError):
    """Conflicto con el estado actual del recurso (409)."""

    code = StandardResponseCode.HTTP_409

    def __init__(
        self, *, msg: str = "Conflicto", data: Any = None, background: BackgroundTask | None = None
    ) -> None:
        super().__init__(msg=msg, data=data, background=background)


class ServerError(BaseExceptionError):
    """Error interno del servidor (500)."""

    code = StandardResponseCode.HTTP_500

    def __init__(
        self,
        *,
        msg: str = "Error interno del servidor",
        data: Any = None,
        background: BackgroundTask | None = None,
    ) -> None:
        super().__init__(msg=msg, data=data, background=background)
