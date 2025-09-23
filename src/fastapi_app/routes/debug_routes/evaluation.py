from typing import Any

from fastapi import APIRouter

router = APIRouter()


@router.post('/evaluate')
async def evaluate(request: Any):
    pass
