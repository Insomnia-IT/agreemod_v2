import logging

import uvicorn
import venusian

from fastapi import APIRouter, FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.background import BackgroundTasks

# from starlette.middleware import Middleware
# from starlette.middleware.cors import CORSMiddleware
# from starlette.middleware.errors import ServerErrorMiddleware
# from starlette.middleware.trustedhost import TrustedHostMiddleware
from traceback_with_variables import print_exc

from app.config import config, traceback_format
from app.errors import RepresentativeError, intake_validation_error_handler


logger = logging.getLogger(__name__)


api_router = APIRouter()


async def server_error_handler(_: Request, e: Exception):
    bg_tasks = BackgroundTasks()
    # if config.SMTP_LOG_ENABLED:
    #     bg_tasks.add_task(send_traceback)

    if config.DEBUG:
        print_exc(fmt=traceback_format)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content="Something went wrong",
        background=bg_tasks,
    )


def get_app() -> FastAPI:
    venusian.Scanner().scan(__import__("app"))

    docs_url = f"{config.API_PREFIX}/_docs" if config.DEBUG else None
    redoc_url = f"{config.API_PREFIX}/_redoc" if config.DEBUG else None

    app = FastAPI(
        title=config.TITLE,
        debug=config.DEBUG,
        openapi_url=f"{config.API_PREFIX}/openapi.json",
        docs_url=docs_url,
        redoc_url=redoc_url,
        version=config.version,
        description=config.DESCRIPTION,
    )
    # app.add_middleware(
    #     Middleware(
    #         CORSMiddleware,
    #         allow_credentials=True,
    #         allow_origins=config.cors_origins,
    #         allow_origin_regex=config.cors_origin_regex,
    #         allow_methods=config.cors_methods,
    #         allow_headers=config.cors_headers,
    #     )
    # )
    # app.add_middleware(Middleware(TrustedHostMiddleware, allowed_hosts=config.allowed_hosts))
    # # todo:
    # #   log user actions middleware: Middleware(LogUserActionMiddleware),
    # #   send log error to sentry or some another collector: Middleware(SentryMiddleware) (custom)
    # app.add_middleware(Middleware(ServerErrorMiddleware, handler=server_error_handler))

    app.include_router(api_router, prefix=config.API_PREFIX)

    @app.exception_handler(RepresentativeError)
    def exception_handler(request, ex: RepresentativeError):  # noqa
        return JSONResponse(status_code=ex.status_code, content=ex.dict())

    @app.exception_handler(RequestValidationError)
    def intake_schema_validation_error_handler(request, exc):
        validation_errors = intake_validation_error_handler(exc)
        return JSONResponse(content=validation_errors, status_code=422)

    return app


if __name__ == "__main__":
    uvicorn.run(
        "app.main:get_app",
        factory=True,
        host=config.API_HOST,
        port=config.API_PORT,
        reload=True,
    )
