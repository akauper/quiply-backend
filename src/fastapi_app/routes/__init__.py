from fastapi import APIRouter

from .debug_routes import router as debug_router
from .scenario import router as scenario_router
from .user import router as user_router

router = APIRouter()
router.include_router(debug_router, prefix='/debug')
router.include_router(scenario_router, prefix='/scenario')
router.include_router(user_router, prefix='/user')
