from fastapi import APIRouter, HTTPException, UploadFile, File, status

from src.models import UserProfile, AccountData
from src.services import storage_service
from src.utils import logger
from src.utils.logging import loggers
from .models import UpdateUserProfileRequest

router = APIRouter()


@router.patch('/update', response_model=AccountData)
async def update_user_profile_route(request: UpdateUserProfileRequest):
    loggers.fastapi.info(f"update_user_profile_route request: {request.user_id} {request.updated_fields}")
    try:
        updated_fields = request.updated_fields
        updated_user = storage_service.update_user_profile(request.user_id, **updated_fields)
        return updated_user.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)


@router.post('/image', status_code=status.HTTP_201_CREATED)
async def upload_image_route(user_id: str, image: UploadFile = File(...)):
    loggers.fastapi.info(f"upload_image_route request: {user_id} | {image.filename}")
    try:
        content = await image.read()
        mime_type = image.content_type

        image_url = storage_service.upload_user_profile_image(user_id, mime_type, content)
        storage_service.update_user_profile(user_id, **{'image_url': image_url})
        return {'image_url': image_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)