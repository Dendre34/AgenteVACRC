import logging

from fastapi import APIRouter, BackgroundTasks, Depends

from app.core.response_schema import ResponseSchemaModel, response_base
from app.core.security import verify_api_token
from app.schemas.contact import ContactRequest, ContactResponse
from app.services.email_service import send_contact_email

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/contact", tags=["contact"])


@router.post(
    "/send-email",
    response_model=ResponseSchemaModel[ContactResponse],
    dependencies=[Depends(verify_api_token)],
)
async def send_email(
    data: ContactRequest, background_tasks: BackgroundTasks
) -> ResponseSchemaModel[ContactResponse]:
    logger.info("Solicitud de contacto recibida: nombre='%s', servicio='%s'", data.nombre, data.servicio)
    background_tasks.add_task(send_contact_email, data)
    return response_base.success(
        data=ContactResponse(message="El correo se enviará en segundo plano.")
    )
