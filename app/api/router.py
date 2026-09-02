from fastapi import APIRouter

from app.api.routes import contact

api_router = APIRouter()
api_router.include_router(contact.router)
