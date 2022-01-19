from fastapi import APIRouter

from core.factory.cloudauth import get_current_auth
from core.factory.web import get_current_app

router = APIRouter()


def init_router():
    app = get_current_app()
    _ = get_current_auth()

    app.include_router(
        router,
        prefix="/metadata",
        tags=["[C00] Public"]
    )
