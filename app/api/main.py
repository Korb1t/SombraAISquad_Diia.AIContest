from fastapi import APIRouter

from app.api.routes import utils, classify, service_resolve

api_router = APIRouter()

api_router.include_router(utils.router)
api_router.include_router(classify.router)
api_router.include_router(service_resolve.router)