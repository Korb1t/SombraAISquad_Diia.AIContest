from fastapi import APIRouter

from app.api.routes import health, classify, service_resolve, voice, appeal, solve_problem


api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(classify.router)
api_router.include_router(service_resolve.router)
api_router.include_router(voice.router)
api_router.include_router(solve_problem.router)
api_router.include_router(appeal.router)
