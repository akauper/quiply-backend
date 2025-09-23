import asyncio
import uuid
from typing import Dict

from fastapi import APIRouter

from src.framework import TextGenerationParams, TextGenerator
from src.utils import loggers
from .models import DebugRespondRequest

router = APIRouter()

task_queue = asyncio.Queue()
task_results: Dict[str, str] = {}


async def debug_worker():
    while True:
        task_id, request = await task_queue.get()
        try:
            text_generator = TextGenerator(generation_params=TextGenerationParams(
                temperature=0.4,
                max_tokens=200,
                stop=[f"{request.user_name}:"]))

            response = await text_generator.run_async(f"""
            Respond Concisely
            {request.message_history}
            {request.user_name}:
            """)

            task_results[task_id] = response.content
        except Exception as e:
            task_results[task_id] = f"An error occurred: {e}"


# This function is called by the debug router.
@router.post('/')
async def debug_respond_route(request: DebugRespondRequest):
    loggers.fastapi.debug(f"debug_response_route Received request: {request}")

    # Generate a unique task ID.
    task_id = str(uuid.uuid4())

    # Put the task into the queue.
    task_queue.put_nowait((task_id, request))

    # Wait until the task is done.
    while task_id not in task_results:
        await asyncio.sleep(0.1)

    # Return the task's response.
    response = task_results.pop(task_id)

    loggers.fastapi.debug(f"debug_response_route Returning response: {response}")

    return response
