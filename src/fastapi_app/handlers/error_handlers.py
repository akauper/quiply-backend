import traceback

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException
from fastapi import Request

from src.utils import loggers


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    loggers.fastapi.exception(f"An error occurred while validating the request: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": "Error occurred while validating the request."},
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    loggers.fastapi.exception(f"An HTTPException occurred with status code {exc.status_code} and detail {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": 'Error occurred while processing the request. Please try again later.'},
    )


async def general_exception_handler(request: Request, exc: Exception):
    traceback_string = "".join(traceback.format_exception(None, exc, exc.__traceback__))
    # Log the traceback for debugging purposes; adjust logging as needed for your application
    print(traceback_string)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
    )
