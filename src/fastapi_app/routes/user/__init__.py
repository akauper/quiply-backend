from fastapi import APIRouter

from .account_router import router as account_router
from .profile_router import router as profile_router

router = APIRouter()
router.include_router(account_router, prefix='/account')
router.include_router(profile_router, prefix='/profile')
