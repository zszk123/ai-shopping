from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class AppError(Exception):
    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code


async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=200,
        content={"code": exc.code, "msg": exc.message, "data": None},
    )


async def unhandled_error_handler(_: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=200,
        content={"code": 500, "msg": "Internal server error", "data": None},
    )


async def validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    first_error = exc.errors()[0] if exc.errors() else {}
    field_path = ".".join(str(item) for item in first_error.get("loc", []) if item != "body")
    detail = first_error.get("msg", "Invalid request parameters")
    msg = f"{field_path}: {detail}" if field_path else detail
    return JSONResponse(
        status_code=200,
        content={"code": 422, "msg": msg, "data": None},
    )
