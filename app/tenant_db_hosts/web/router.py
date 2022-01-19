from fastapi import APIRouter, Depends

from app.user_roles import Roles
from core.factory.cloudauth import get_current_auth
from core.factory.web import get_current_app
from web.core.tenants import workspace_header

router_superadmin_single = APIRouter()
router_superadmin_plural = APIRouter()


def init_router():
    app = get_current_app()
    auth = get_current_auth()

    app.include_router(
        router_superadmin_single,
        prefix="/superadmin/db-host",
        tags=["[SA01] SuperAdmin / Tenant DB Hosts"],
        dependencies=[
            Depends(workspace_header),
            Depends(auth.allow([Roles.SUPER_ADMIN], "SuperAdmin / Tenant DB Hosts"))
        ]
    )

    app.include_router(
        router_superadmin_plural,
        prefix="/superadmin/db-hosts",
        tags=["[SA01] SuperAdmin / Tenant DB Hosts"],
        dependencies=[
            Depends(workspace_header),
            Depends(auth.allow([Roles.SUPER_ADMIN], "SuperAdmin / Tenant DB Hosts"))
        ]
    )
