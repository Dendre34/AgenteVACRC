from dataclasses import dataclass
from enum import Enum


class CustomCodeBase(Enum):
    """Clase base para códigos de estado personalizados."""

    @property
    def code(self) -> int:
        return self.value[0]

    @property
    def msg(self) -> str:
        return self.value[1]


class CustomResponseCode(CustomCodeBase):
    """Códigos de respuesta usados por ResponseBase."""

    HTTP_200 = (200, "Solicitud exitosa")
    HTTP_400 = (400, "Solicitud incorrecta")
    HTTP_401 = (401, "No autorizado")
    HTTP_403 = (403, "Acceso prohibido")
    HTTP_404 = (404, "Recurso no encontrado")
    HTTP_422 = (422, "Error de validación de datos")
    HTTP_500 = (500, "Error interno del servidor")


@dataclass
class CustomResponse:
    """Código/mensaje de respuesta abierto, útil cuando el mensaje es dinámico."""

    code: int
    msg: str


class StandardResponseCode:
    """Subconjunto de códigos HTTP estándar usados por las excepciones tipadas."""

    HTTP_400 = 400
    HTTP_401 = 401
    HTTP_403 = 403
    HTTP_404 = 404
    HTTP_409 = 409
    HTTP_422 = 422
    HTTP_500 = 500
