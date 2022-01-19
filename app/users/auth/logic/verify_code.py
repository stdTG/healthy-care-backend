import datetime

from fastapi import Request

import app.users.common.models.db as dbm
from core.utils.random import Random
from ..web_model import (CredentialStatusEnum, MobileAuthVerifyCode, MobileAuthVerifyCodeOut)


async def verify_code_handler(data: MobileAuthVerifyCode, request: Request):
    print(f"[VERIFY-CODE] UserVerification")
    verification: dbm.UserVerification = dbm.UserVerification.objects(
        token=data.verification_token).first()

    if not verification:
        print(f"[VERIFY-CODE] Invalid Token")

        return MobileAuthVerifyCodeOut(
            status=CredentialStatusEnum.TOKEN_INVALID,
        )

    if datetime.datetime.utcnow() > verification.tokenExpires:
        print(f"[VERIFY-CODE] Token expired")
        return MobileAuthVerifyCodeOut(
            status=CredentialStatusEnum.TOKEN_EXPIRED,
        )

    if not (data.code.strip() == verification.code):
        print(f"[VERIFY-CODE] Invalid Code")

        return MobileAuthVerifyCodeOut(
            status=CredentialStatusEnum.CODE_DOESNT_MATCH,
        )

    print(f"[VERIFY-CODE] Updating Patient's verification status")
    secrets = Random().get_verification_secrets()
    verification.token = secrets.token
    verification.status = CredentialStatusEnum.REQUIRE_CHANGE_PASSWORD
    verification.save()

    return MobileAuthVerifyCodeOut(
        status=verification.status,
        updated_verification_token=verification.token,
    )
