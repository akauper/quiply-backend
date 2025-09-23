import random
from typing import List

from fastapi import APIRouter, HTTPException

from src.models import ScenarioInstance, ScenarioResult
from src.scenario import scenario_manager
from src.services import storage_service
from src.utils.logging import loggers
from .models import CreateScenarioRequest, EndScenarioRequest

router = APIRouter()


def replace_random_actors(actor_ids: List[str], eligible_actor_ids: List[str]) -> List[str]:
    if 'random' not in actor_ids:
        return actor_ids

    random_count = actor_ids.count('random')
    actor_ids = [actor_id for actor_id in actor_ids if actor_id != 'random']
    for _ in range(random_count):
        available_actors = [actor for actor in eligible_actor_ids if actor not in actor_ids]
        if available_actors:
            random_actor = random.choice(available_actors)
            actor_ids.append(random_actor)
        else:
            # Handle the case where there are no more available actors to choose from
            loggers.fastapi.error(f'No more available actors to choose from for scenario')
            break


@router.post('/', response_model=ScenarioInstance)
async def create_scenario_instance_route(request: CreateScenarioRequest):
    # print('SCENARIO INSTANCE REQUEST', request.model_dump_json())
    loggers.fastapi.debug(f'ScenarioInstance request: {request.model_dump_json(indent=2)}')
    try:
        # Handle mystery actors in config
        eligible_actor_ids = [actor.uid for actor in storage_service.get_actor_templates()]
        if 'random' in request.scenario_config.actor_ids:
            request.scenario_config.actor_ids = replace_random_actors(request.scenario_config.actor_ids, eligible_actor_ids)
        if 'random' in request.scenario_config.special_actor_ids:
            request.scenario_config.special_actor_ids = replace_random_actors(request.scenario_config.special_actor_ids, eligible_actor_ids)

        account_data = storage_service.get_account_data(request.user_id)

        instance = storage_service.create_scenario_instance(ScenarioInstance(
            account_data=account_data,
            scenario_config=request.scenario_config,
        ))
        scenario_manager.create_scenario(instance, request.overrideSettings)
        return instance
    except Exception as e:
        loggers.fastapi.exception(e)
        return HTTPException(status_code=500, detail=e)


@router.post('/force-end', response_model=bool)
async def force_end_scenario_route(request: EndScenarioRequest):
    try:
        loggers.fastapi.debug(f'Force ending scenario for user {request.user_id}')
        await scenario_manager.end_scenario_async(request.scenario_instance_id, False)
        return True
    except Exception as e:
        loggers.fastapi.exception(e)
        return HTTPException(status_code=500, detail=e)


@router.post('/complete', response_model=ScenarioResult)
async def complete_scenario_route(request: EndScenarioRequest):
    try:
        loggers.fastapi.debug(f'Ending complete scenario for user {request.user_id}')
        result = await scenario_manager.end_scenario_async(request.scenario_instance_id, True)
        if result is None:
            return HTTPException(status_code=404, detail="Scenario not found")
        return result
    except Exception as e:
        loggers.fastapi.exception(e)
        return HTTPException(status_code=500, detail=e)

