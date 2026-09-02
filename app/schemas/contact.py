from pydantic import BaseModel, Field


class ContactRequest(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=150)
    telefono: str = Field(..., min_length=1, max_length=30)
    servicio: str = Field(..., min_length=1, max_length=150)
    mensaje: str = Field(..., min_length=1, max_length=2000)


class ContactResponse(BaseModel):
    message: str
