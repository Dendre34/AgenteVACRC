from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

from app.core.response_code import CustomResponse, CustomResponseCode

SchemaT = TypeVar("SchemaT")


class ResponseModel(BaseModel):
    """Modelo de respuesta unificado sin schema de datos específico."""

    code: int = Field(CustomResponseCode.HTTP_200.code, description="Código de respuesta")
    msg: str = Field(CustomResponseCode.HTTP_200.msg, description="Mensaje de respuesta")
    data: Any | None = Field(None, description="Datos de respuesta")


class ResponseSchemaModel(ResponseModel, Generic[SchemaT]):
    """Modelo de respuesta unificado con schema de datos tipado."""

    data: SchemaT


class ResponseBase:
    """Métodos unificados para construir respuestas de éxito y error."""

    @staticmethod
    def _response(
        *, res: CustomResponseCode | CustomResponse, data: Any | None
    ) -> ResponseModel | ResponseSchemaModel[Any]:
        if data is None:
            return ResponseModel(code=res.code, msg=res.msg, data=data)
        return ResponseSchemaModel[Any](code=res.code, msg=res.msg, data=data)

    def success(
        self,
        *,
        res: CustomResponseCode | CustomResponse = CustomResponseCode.HTTP_200,
        data: Any | None = None,
    ) -> ResponseModel | ResponseSchemaModel[Any]:
        return self._response(res=res, data=data)

    def fail(
        self,
        *,
        res: CustomResponseCode | CustomResponse = CustomResponseCode.HTTP_400,
        data: Any | None = None,
    ) -> ResponseModel | ResponseSchemaModel[Any]:
        return self._response(res=res, data=data)


response_base: ResponseBase = ResponseBase()
