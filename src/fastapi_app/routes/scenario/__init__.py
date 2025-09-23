from fastapi import APIRouter

from .config_router import router as config_router
from .instance_router import router as instance_router
from .context_router import router as context_router

router = APIRouter()
router.include_router(config_router, prefix='/config')
router.include_router(instance_router, prefix='/instance')
router.include_router(context_router, prefix='/context_reference')
