from fastapi import APIRouter, Depends

from app.user_roles import Roles
from core.factory.cloudauth import get_current_auth
from core.factory.web import get_current_app
from web.core.tenants import workspace_header

router_superadmin = APIRouter()


def init_router():
    app = get_current_app()
    auth = get_current_auth()

    app.include_router(
        router_superadmin,
        prefix="/superadmin",
        tags=["[SA01] SuperAdmin / Migrations"],
        dependencies=[
            Depends(workspace_header),
            Depends(auth.allow([Roles.SUPER_ADMIN], "SuperAdmin / Migrations"))
        ]
    )
