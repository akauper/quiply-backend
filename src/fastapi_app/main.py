import asyncio
from typing import List, Callable, Optional

from devtools import debug
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError, HTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from starlette.websockets import WebSocket

from src.settings import quiply_settings, FastAPISettings
from src.scenario import scenario_manager
from src.websocket.error_handler import handle_websocket_exception
from ..exceptions import BaseWebsocketException

from .routes import router as api_router
from .routes.debug_routes.llm_response_router import debug_worker
from .middlewares import FirebaseAuthMiddleware

from .handlers import validation_exception_handler, http_exception_handler, general_exception_handler


class QuiplyAPI(FastAPI):
    settings: FastAPISettings
    prefix: str = f"/api/v{quiply_settings.fastapi.version}"
    _startup_callbacks: List[Callable]

    def __init__(self, startup_callbacks: List[Callable], **kwargs):
        super().__init__(**kwargs)

        self.settings: FastAPISettings = quiply_settings.fastapi
        self._startup_callbacks = startup_callbacks if startup_callbacks else []

        self.register_middlewares()
        self.handle_exceptions()
        self.include_router(api_router, prefix=self.prefix)

        @self.get("/health")
        async def health():
            return JSONResponse(content="healthy")

        @self.get("/healthcheck", include_in_schema=False)
        async def healthcheck() -> dict[str, str]:
            return {"status": "ok"}

        @self.websocket("/ws/{client_id}/{scenario_instance_id}")
        async def websocket_endpoint(websocket: WebSocket, client_id: str, scenario_instance_id: str):
            await scenario_manager.start_scenario_async(websocket, scenario_instance_id)

        @self.on_event("startup")
        async def startup_event():
            asyncio.create_task(debug_worker())
            for callback in self._startup_callbacks:
                callback()

    def register_middlewares(self):
        self.add_middleware(
            CORSMiddleware,
            allow_origins=self.settings.cors_origins,
            # allow_origin_regex=self.config.cors_origins_regex,
            allow_credentials=True,
            allow_methods=self.settings.cors_methods,
            allow_headers=self.settings.cors_headers,
        )

        self.add_middleware(FirebaseAuthMiddleware)

    def handle_exceptions(self):
        self.add_exception_handler(BaseWebsocketException, handle_websocket_exception)

        self.add_exception_handler(RequestValidationError, validation_exception_handler)
        self.add_exception_handler(HTTPException, http_exception_handler)
        self.add_exception_handler(Exception, general_exception_handler)


def get_application(startup_callbacks: Optional[List[Callable]] = None) -> QuiplyAPI:
    return QuiplyAPI(startup_callbacks, **quiply_settings.fastapi.fastapi_kwargs)

# if debug_tests_enabled():
#     execute_all_tests('interview')
