from fastapi import APIRouter

from .llm_response_router import router as llm_response_router
from .evaluation import router as evaluation_router

router = APIRouter()
router.include_router(llm_response_router, prefix='/respond')
router.include_router(evaluation_router, prefix='/evaluation')
