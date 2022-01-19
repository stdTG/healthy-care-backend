from fastapi import APIRouter, Depends

from app.user_roles import Roles
from core.factory.cloudauth import get_current_auth
from core.factory.web import get_current_app
from web.core.tenants import workspace_header

router_mobile = APIRouter()


def init_router():

    app = get_current_app()
    auth = get_current_auth()

    app.include_router(
        router_mobile,
        prefix="/mobile/appointment",
        tags=["[M02] Mobile / Appointments"],
        dependencies=[
            Depends(workspace_header),
            Depends(auth.allow(Roles.ADMINS_AND_PATIENT, "Mobile / Health Center (org. units)")),
        ]
    )
