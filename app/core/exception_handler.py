import logging

from http import HTTPStatus

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.exceptions import HTTPException

from app.core.config import settings
from app.core.errors import BaseExceptionError
from app.core.response_code import CustomResponseCode, StandardResponseCode
from app.core.response_schema import response_base

logger = logging.getLogger(__name__)


def _get_exception_code(status_code: int) -> int:
    """Garantiza que el código a usar como status HTTP de la respuesta sea válido."""
    try:
        HTTPStatus(status_code)
    except ValueError:
        return StandardResponseCode.HTTP_400
    return status_code


async def _validation_exception_handler(exc: RequestValidationError | ValidationError) -> JSONResponse:
    """Maneja tanto errores de validación de FastAPI como de Pydantic."""
    errors = exc.errors()
    error = errors[0]
    error_msg = error.get("msg")
    if settings.ENVIRONMENT == "dev":
        field = str(error.get("loc", [""])[-1])
        message = f"{field}: {error_msg} (recibido: {error.get('input')!r})"
    else:
        message = error_msg
    content = {
        "code": StandardResponseCode.HTTP_422,
        "msg": f"Parámetros de solicitud inválidos: {message}",
        "data": {"errors": errors} if settings.ENVIRONMENT == "dev" else None,
    }
    return JSONResponse(status_code=StandardResponseCode.HTTP_422, content=content)


def register_exception(app: FastAPI) -> None:
    """Registra los manejadores de excepciones globales de la aplicación."""

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        if settings.ENVIRONMENT == "dev":
            content = {"code": exc.status_code, "msg": exc.detail, "data": None}
        else:
            content = response_base.fail(res=CustomResponseCode.HTTP_400).model_dump()
        return JSONResponse(
            status_code=_get_exception_code(exc.status_code),
            content=content,
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def fastapi_validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        return await _validation_exception_handler(exc)

    @app.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
        return await _validation_exception_handler(exc)

    @app.exception_handler(BaseExceptionError)
    async def custom_exception_handler(request: Request, exc: BaseExceptionError) -> JSONResponse:
        content = {"code": exc.code, "msg": str(exc.msg), "data": exc.data}
        return JSONResponse(
            status_code=_get_exception_code(exc.code),
            content=content,
            background=exc.background,
        )

    @app.exception_handler(Exception)
    async def all_unknown_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Excepción no controlada en %s", request.url.path)
        if settings.ENVIRONMENT == "dev":
            content = {"code": StandardResponseCode.HTTP_500, "msg": str(exc), "data": None}
        else:
            content = response_base.fail(res=CustomResponseCode.HTTP_500).model_dump()
        return JSONResponse(status_code=StandardResponseCode.HTTP_500, content=content)
