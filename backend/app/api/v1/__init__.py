from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.missions import router as missions_router
from app.api.v1.vehicles import router as vehicles_router
from app.api.v1.loads import router as loads_router
from app.api.v1.agent import router as agent_router
from app.api.v1.checkpoints import router as checkpoints_router
from app.api.v1.ai import router as ai_router
from app.api.v1.maps import router as maps_router
from app.api.v1.demo import router as demo_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(missions_router)
api_router.include_router(vehicles_router)
api_router.include_router(loads_router)
api_router.include_router(agent_router)
api_router.include_router(checkpoints_router)
api_router.include_router(ai_router)
api_router.include_router(maps_router)
api_router.include_router(demo_router)
