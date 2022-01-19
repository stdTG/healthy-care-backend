from fastapi import APIRouter, Depends

from app.user_roles import Roles
from core.factory.cloudauth import get_current_auth
from core.factory.web import get_current_app
from web.core.tenants import workspace_header

router_init_master = APIRouter()
router_common_single = APIRouter()
router_public_single = APIRouter()
router_superadmin_plural = APIRouter()


def init_router():
    app = get_current_app()
    auth = get_current_auth()

    app.include_router(
        router_common_single,
        prefix="/workspace",
        tags=["[C02] Authenticated"],
        dependencies=[
            Depends(workspace_header),
            Depends(auth.allow([Roles.ALL_AUTHENTICATED], "Common / Tenant Workspaces"))
        ]
    )

    app.include_router(
        router_init_master,
        prefix="/superadmin/workspace",
        tags=["[SA01] SuperAdmin / Tenant Workspaces"],
        dependencies=[
        ]
    )

    app.include_router(
        router_public_single,
        prefix="/workspace",
        tags=["[C00] Public"]
    )

    app.include_router(
        router_superadmin_plural,
        prefix="/superadmin/workspaces",
        tags=["[SA01] SuperAdmin / Tenant Workspaces"],
        dependencies=[
            Depends(workspace_header),
            Depends(auth.allow([Roles.SUPER_ADMIN], "SuperAdmin / Tenant Workspaces"))
        ]
    )
