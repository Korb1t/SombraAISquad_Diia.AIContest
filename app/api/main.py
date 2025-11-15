from fastapi import APIRouter

from app.api.routes import utils, classify  # Add classify here

api_router = APIRouter()

api_router.include_router(utils.router)
api_router.include_router(classify.router)