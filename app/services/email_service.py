import logging
from datetime import date
from pathlib import Path

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from fastapi_mail.schemas import MultipartSubtypeEnum
from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.core.config import settings
from app.schemas.contact import ContactRequest

logger = logging.getLogger(__name__)

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates" / "email"
LOGO_PATH = Path(__file__).resolve().parent.parent / "static" / "email" / "logo.png"
LOGO_CID = "logo"

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.USE_CREDENTIALS,
    VALIDATE_CERTS=settings.VALIDATE_CERTS,
)

jinja_env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=select_autoescape(["html"]),
)


def _render_contact_html(data: ContactRequest) -> str:
    template = jinja_env.get_template("contact.html")
    return template.render(
        nombre=data.nombre,
        telefono=data.telefono,
        servicio=data.servicio,
        mensaje=data.mensaje,
        anio=date.today().year,
    )


async def send_contact_email(data: ContactRequest) -> None:
    message = MessageSchema(
        subject=f"Nuevo contacto: {data.servicio}",
        recipients=[settings.MAIL_RECIPIENT],
        body=_render_contact_html(data),
        subtype=MessageType.html,
        multipart_subtype=MultipartSubtypeEnum.related,
        attachments=[
            {
                "file": str(LOGO_PATH),
                "headers": {
                    "Content-ID": f"<{LOGO_CID}>",
                    "Content-Disposition": "inline",
                },
                "mime_type": "image",
                "mime_subtype": "png",
            }
        ],
    )

    fm = FastMail(conf)
    try:
        await fm.send_message(message)
    except Exception:
        logger.exception("Error al enviar el correo de contacto para el servicio '%s'", data.servicio)
