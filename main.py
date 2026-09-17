import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from routes import (document, face, health, plate)
from core import config
from core.config import Settings
from reports.logs_config import config_logging

config_logging()
logger = logging.getLogger(__name__)
settings = config.get_settings()

class BodySizeLimit(BaseHTTPMiddleware):
    def __init__(self, app2, max_bytes: int)->None:
        super().__init__(app2)
        self.max_bytes = max_bytes

    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_bytes:
            return JSONResponse(status_code=status.HTTP_413_CONTENT_TOO_LARGE, content={"detail": "Body too large"})
        return await call_next(request)

app = FastAPI(title=Settings.service_name, version="0.0.1", docs_url="/docs" if settings.environment != "production" else None, redoc_url=None)

app.add_middleware(BodySizeLimit, max_bytes = Settings.max_upload + 1024)

app.include_router(document.router)
app.include_router(face.router)
app.include_router(health.router)
app.include_router(plate.router)

@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception)->JSONResponse:
    logger.exception("Error no found in %s", request.url.path)
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": "Internal server error"})


