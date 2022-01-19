import datetime

from fastapi import Request

import app.users.common.models.db as dbm
from app.tenant_workspaces.model_db import Workspace
from app.users.dashboard.logic.verification_helper import VerificationHelper
from core.errors import *
from core.utils.random import Random
from ..web_model import CredentialStatusEnum, MobileAuthVerifyUsernameOut, MobileAuthVerifyUsernameIn


async def verify_username_handler(data: MobileAuthVerifyUsernameIn, helper: VerificationHelper,
                                  request: Request):
    print(f"[VERIFY-ATTRIBUTE] Lookup Workspace")
    wks: Workspace = await helper.lookup_workspace(data.username, request)
    print(f"[VERIFY-ATTRIBUTE] Workspace: {wks.short_name}")

    verification: dbm.UserVerification = dbm.UserVerification.objects(
        username=data.username).first()
    if not verification:
        raise HTTPNotFoundError(f"Verification tokens not found [{data.username}]")
    print(f"[VERIFY-ATTRIBUTE] DbUserVerification {str(verification)}")

    if verification and verification.status == CredentialStatusEnum.VERIFIED:
        return MobileAuthVerifyUsernameOut(
            status=CredentialStatusEnum.VERIFIED,
            verification_token=None,
        )

    if data.reset:
        secrets = Random().get_verification_secrets()
        verification.code = secrets.code
        verification.attempts = 0
        verification.token = secrets.token
        verification.tokenExpires = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
        verification.status = CredentialStatusEnum.REQUIRE_VERIFICATION
        verification.save()

    if data.reset or verification.status == CredentialStatusEnum.REQUIRE_VERIFICATION:
        verification.status = CredentialStatusEnum.REQUIRE_CODE
        verification.save()
        helper.send_code_to_user(verification.username, "Alakine Verification",
                                 f"Your verification code is: {verification.code}",
                                 message_html=f"<html><body>Your verification code is: <strong>"
                                              f"{verification.code}</strong> </body></html>"
                                 )

    return MobileAuthVerifyUsernameOut(
        status=verification.status,
        verification_token=verification.token,
    )
