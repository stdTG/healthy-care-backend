from datetime import datetime

from app.sendbird.model_web import SendbirdUserOut
from app.tenant_workspaces.model_db import Workspace
from app.users.common.models.db import DashboardUser as User, SendbirdSettings
from app.users.dashboard.logic.patient.create import create_sendbird_user
from core.sendbird.users import SendbirdUsers
from core.utils.transaction_async import TransactionAsync
from web.cloudauth.auth_claims import AuthClaims


async def sendbird_dashboard_user_auth_handler(wks: Workspace, current_user: AuthClaims):
    db_user = User.objects(cognito_sub=current_user.sub).first()
    if not db_user.sendbird:
        async with TransactionAsync("userUpdateSendbird") as trx:
            db_user = await create_sendbird_user(db_user, wks, trx=trx)
            db_user.save()

    users_client = SendbirdUsers(wks.sendbird.app_id, wks.sendbird.master_api_token)
    result = await users_client.update(user_id=current_user.sub, issue_access_token=True,
                                       issue_session_token=True)
    if "error" in result.data:
        async with TransactionAsync("userUpdateSendbird") as trx:
            await create_sendbird_user(db_user, wks, trx=trx)
            db_user.save()
    else:
        sendbird: SendbirdSettings = db_user.sendbird

        sendbird.access_token = result.data["access_token"]
        sendbird.session_tokens = result.data["session_tokens"]
        db_user.save()

    response = SendbirdUserOut(
        app_id=wks.sendbird.app_id,
        access_token=db_user.sendbird.access_token,
        session_token=db_user.sendbird.session_tokens[0]["session_token"],
        session_token_expired=datetime.fromtimestamp(
            db_user.sendbird.session_tokens[0]["expires_at"]/1000).strftime('%Y-%m-%d %H:%M:%S'),
    )

    return response
