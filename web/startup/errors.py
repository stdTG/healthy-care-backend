from fastapi import Request
from fastapi.responses import JSONResponse

from core.errors import HTTPNotFoundError, NoPermissionsError
from core.factory.web import get_current_app
from core.utils.logging import Logger


def init_error_handling():
    print("[APP] Init Error Handlers")

    app = get_current_app()
    logger = Logger()

    @app.exception_handler(NoPermissionsError)
    def handle_no_permissions_error(request: Request, error: NoPermissionsError):
        logger.error(error)
        return JSONResponse(
            status_code=403,
            content={
                "error": {
                    "code": 403,
                    "message": f"You don't have  permissions to access this resource.",
                    "details": [],
                }
            }

        )

    @app.exception_handler(HTTPNotFoundError)
    def handle_not_found_error(request: Request, error: HTTPNotFoundError):
        logger.error(error)
        return JSONResponse(
            status_code=404,
            content={
                "error": {
                    "code": 404,
                    "message": str(error.detail),
                    "details": [],
                }
            }
        )

    @app.exception_handler(422)
    def handle_not_found_error(request: Request, error: HTTPNotFoundError):
        logger.error(error)
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": 422,
                    "message": str(error.detail),
                    "details": [],
                }
            }
        )

    @app.exception_handler(Exception)
    def handle_http_error(request: Request, error: Exception):
        logger.error(error)
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": 500,
                    "message": str(error),
                    "details": [],
                }
            }
        )
