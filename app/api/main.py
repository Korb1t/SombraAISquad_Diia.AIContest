from fastapi import APIRouter

from app.api.routes import utils, classify, voice

api_router = APIRouter()

api_router.include_router(utils.router)
api_router.include_router(classify.router)
api_router.include_router(voice.router)