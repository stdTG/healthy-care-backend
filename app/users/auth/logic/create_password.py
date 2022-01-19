from fastapi import Request

import app.users.common.models.db as dbm
from app.context import get_current_workspace
from app.tenant_workspaces.model_db import Workspace
from core.utils.aws import get_cognito_idp
from ..web_model import CredentialStatusEnum, MobileAuthCreatePasswordIn


async def create_password_handler(data: MobileAuthCreatePasswordIn,
                                  request: Request) -> CredentialStatusEnum:
    wks: Workspace = await get_current_workspace(request)

    verification: dbm.UserVerification = dbm.UserVerification.objects(
        token=data.updated_verification_token).first()

    if not verification:
        return CredentialStatusEnum.TOKEN_INVALID

    _ = get_cognito_idp().admin_set_user_password(
        UserPoolId=wks.cognito.user_pool_id,
        Username=verification.username,
        Password=data.password,
        Permanent=True,
    )

    verification.code = None
    verification.token = None
    verification.status = CredentialStatusEnum.VERIFIED
    verification.save()

    return CredentialStatusEnum.VERIFIED
