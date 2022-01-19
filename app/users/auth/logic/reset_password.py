import datetime

from app.users.auth.web_model import CredentialStatusEnum, MobileAuthVerifyUsernameOut
from app.users.common.models.db import UserVerification
from app.users.dashboard.logic.verification_helper import VerificationHelper
from core.utils.random import Random


async def reset_password_handler(username: str, id_: str, type_, helper: VerificationHelper):
    data = Random.get_verification_secrets()
    obj = UserVerification()

    obj.user_id = id_
    obj.type_ = type_
    obj.username = username
    obj.token = data.token
    obj.tokenExpires = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
    obj.code = data.code
    obj.attempts = 0
    obj.status = CredentialStatusEnum.REQUIRE_CODE
    obj.save()

    helper.send_code_to_user(obj.username, "Alakine Verification",
                             f"Your verification code is: {obj.code}",
                             message_html=f"<html><body>Your verification code is: <strong>"
                                          f"{obj.code}</strong> </body></html>"
                             )

    return MobileAuthVerifyUsernameOut(
        status=obj.status,
        verification_token=obj.token,
    )
