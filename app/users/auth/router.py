from fastapi import APIRouter, Depends

from core.factory.cloudauth import get_current_auth
from core.factory.web import get_current_app
from web.core.tenants import workspace_header

router_mobile_auth_public = APIRouter()
router_public = APIRouter()


def init_router():
    app = get_current_app()
    _ = get_current_auth()

    app.include_router(
        router_mobile_auth_public,
        prefix="/mobile/auth",
        tags=["[M00] Registration & Authentication"]
    )

    app.include_router(
        router_public,
        prefix="",
        tags=["[C00] Public"],
        dependencies=[
            Depends(workspace_header),
        ]
    )
