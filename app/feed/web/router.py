from fastapi import APIRouter, Depends

from app.user_roles import Roles
from core.factory.cloudauth import get_current_auth
from core.factory.web import get_current_app
from web.core.tenants import workspace_header

router_tests_questions = APIRouter()
router_questions = APIRouter()


def init_router():
    app = get_current_app()
    auth = get_current_auth()

    app.include_router(
        router_tests_questions,
        prefix="/feed/tests/questions",
        tags=["[M03] Feed Tests / Questions"],
        dependencies=[
            Depends(workspace_header),
            Depends(auth.allow(Roles.ADMINS_AND_PATIENT, "Feed Tests / Questions")),
        ]
    )

    app.include_router(
        router_questions,
        prefix="/feed/questions",
        tags=["[M03] Feed / Questions"],
        dependencies=[
            Depends(workspace_header),
            Depends(auth.allow(Roles.ADMINS_AND_PATIENT, "Feed / Questions")),
        ]
    )
