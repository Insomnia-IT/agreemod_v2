import logging

import uvicorn
import venusian

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.background import BackgroundTasks
from traceback_with_variables import print_exc

from app.config import config, traceback_format
from app.errors import RepresentativeError, intake_validation_error_handler
from app.routers.people import router as router_people
from app.routers.places import router as router_directions


logger = logging.getLogger(__name__)


async def server_error_handler(_: Request, e: Exception):
    bg_tasks = BackgroundTasks()

    if config.DEBUG:
        print_exc(fmt=traceback_format)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content="Something went wrong",
        background=bg_tasks,
    )


def get_app() -> FastAPI:
    venusian.Scanner().scan(__import__("db"))
    venusian.Scanner().scan(__import__("app"))

    docs_url = f"{config.API_PREFIX}/_docs" if config.DEBUG else None
    redoc_url = f"{config.API_PREFIX}/_redoc" if config.DEBUG else None

    logger.info(f"doc url: {docs_url}")
    app = FastAPI(
        title=config.TITLE,
        debug=config.DEBUG,
        openapi_url=f"{config.API_PREFIX}/openapi.json",
        docs_url=docs_url,
        redoc_url=redoc_url,
        version=config.version,
        description=config.DESCRIPTION,
    )

    # todo:
    #   log user actions middleware: Middleware(LogUserActionMiddleware),
    #   send log error to sentry or some another collector: Middleware(SentryMiddleware) (custom)

    app.include_router(router_people)
    app.include_router(router_directions)

    @app.exception_handler(RepresentativeError)
    def exception_handler(request, ex: RepresentativeError):  # noqa
        return JSONResponse(status_code=ex.status_code, content=ex.dict())

    @app.exception_handler(RequestValidationError)
    def intake_schema_validation_error_handler(request, exc):
        validation_errors = intake_validation_error_handler(exc)
        return JSONResponse(content=validation_errors, status_code=422)

    return app


def run_api():
    logger.debug(
        f"starting... : host={config.API_HOST} port={config.API_PORT} debug={config.DEBUG}"
    )
    uvicorn.run(
        "app.main:get_app",
        factory=True,
        host=config.API_HOST,
        port=config.API_PORT,
        reload=config.DEBUG,
    )


if __name__ == "__main__":
    run_api()
