from fastapi import APIRouter, HTTPException

from src.models import ScenarioConfig
from src.services import storage_service

router = APIRouter()


@router.post('/')
async def create_scenario_config_route(request: ScenarioConfig):
    print(request)
    try:
        storage_service.save_scenario_config(request)
        return True
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)


@router.delete('/{user_id}/{config_name}')
async def delete_scenario_config_route(user_id: str, config_name: str):
    try:
        storage_service.delete_scenario_config(user_id, config_name)
        return {'success': True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)
