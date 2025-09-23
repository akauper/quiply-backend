from devtools import debug
from fastapi import APIRouter, HTTPException

from src.settings import quiply_settings
from src.models import AccountData, UserProfile
from src.services import storage_service
from src.utils.logging import loggers
from .models import CreateAccountDataRequest, UpdateAccountNameRequest, UpdateAccountDataRequest

router = APIRouter()


@router.post('/create', response_model=AccountData)
async def create_account_data_route(request: CreateAccountDataRequest):
    loggers.fastapi.info(f"create_account_data_route request: {request}")
    if quiply_settings.fastapi.allow_registration is False:
        raise HTTPException(status_code=403, detail="Registration is disabled")

    try:
        account_data = AccountData(
            id=request.id,
            created_at=request.created_at,
            updated_at=request.created_at,

            email=request.email,
            first_name=request.first_name,
            last_name=request.last_name,
            birthday=request.birthday,
            image_url=request.image_url,
            phone_number=request.phone_number,

            profile=UserProfile(
                account_id=request.id,
                name=request.first_name + ' ' + request.last_name,
                image_url=request.image_url,
            )
        )
        storage_service.create_account_data(account_data)
        return account_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)


@router.post('/delete', response_model=bool)
async def delete_account_data_route(user_id: str):
    loggers.fastapi.info(f"delete_account_data_route request: {user_id}")
    try:
        storage_service.delete_account_data(user_id)
        return True
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)


@router.patch('/update-name', response_model=bool)
async def update_name_route(request: UpdateAccountNameRequest):
    loggers.fastapi.info(f"update_name_route request: {request}")
    try:
        if request.first_name is None and request.last_name is None:
            return True
        storage_service.set_account_data_first_last_name(request.uid, request.first_name, request.last_name)
        return True
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)


@router.patch('/update', response_model=bool)
async def update_account_data(request: UpdateAccountDataRequest):
    loggers.fastapi.info(f"update_account_data request: {request}")
    try:
        storage_service.update_account_data(request.user_id, request.updated_fields)
        return True
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)


# @router.patch('/update-birthday', response_model=bool)
# async def update_birthday_route(user_id: str, birthday: int):
#     loggers.fastapi.info(f"update_birthday_route request: {user_id} | {birthday}")
#     try:
#         storage_service.set_user_account_birthday(user_id, birthday)
#         return True
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=e)