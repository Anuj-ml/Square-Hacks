from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
import traceback

logger = logging.getLogger(__name__)

async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    logger.error(f"Validation error on {request.url.path}: {exc.errors()}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": "Validation Error",
            "message": "Invalid request data",
            "details": exc.errors(),
            "path": str(request.url.path)
        }
    )

async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException
) -> JSONResponse:
    logger.error(f"HTTP {exc.status_code} on {request.url.path}: {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url.path)
        }
    )

async def general_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    logger.exception(f"Unhandled error on {request.url.path}")
    
    error_detail = str(exc) if hasattr(exc, '__str__') else "Internal server error"
    
    response_content = {
        "success": False,
        "error": "Internal Server Error",
        "message": error_detail,
        "path": str(request.url.path)
    }
    
    try:
        from core.config import settings
        if getattr(settings, 'DEBUG', False):
            response_content["traceback"] = traceback.format_exc()
    except:
        pass
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response_content
    )

def setup_error_handlers(app):
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
