from mongoengine import Document
from fastapi.requests import Request

from app.context import get_current_workspace
from app.tenant_workspaces.model_db import Workspace
from app.users.common.models.db import PatientUser as DbPatientUser
from app.users.dashboard.gql.utils import get_user_name
from core.aws.client import get_cognito_idp
from core.sendbird.group_channels import SendbirdGroupChannels
from core.sendbird.users import SendbirdUsers
from core.utils.transaction import Transaction


def rollback_delete_db_patient(db_object: Document):
    print("[PATIENT-ROLLBACK] DB Patient")
    db_object.save()


def delete_db_patient(id_, trx):
    print("[PATIENT-DELETE] DB Patient")

    db_object: DbPatientUser = DbPatientUser.objects.with_id(id_)
    if not db_object:
        return

    db_object.deleted = True
    db_object.firstName = "Anonymous"
    db_object.lastName = "Patient"
    db_object.save()

    trx.push(rollback_delete_db_patient, db_object)

    return db_object


def disable_cognito_user(db_object, user_pool_id, trx):
    print("[PATIENT-DELETE] Cognito Patient")
    username = get_user_name(db_object.email, db_object.phone)
    cognito_idp = get_cognito_idp()

    result = cognito_idp.admin_disable_user(UserPoolId=user_pool_id, Username=username)
    print("COGNITO User disabled")
    print(result)

    trx.push(rollback_disable_cognito_user, username, user_pool_id)
    return result


def rollback_disable_cognito_user(username, user_pool_id) -> None:
    cognito_idp = get_cognito_idp()
    cognito_idp.admin_enable_user(UserPoolId=user_pool_id, Username=username)


async def delete_patient_handler(id_, request: Request):
    current_workspace: Workspace = await get_current_workspace(request)

    sendbird = current_workspace.sendbird

    with Transaction("PatientDelete") as trx:
        db_object = delete_db_patient(id_, trx)
        if db_object:
            disable_cognito_user(db_object, current_workspace.cognito.user_pool_id,
                                 trx)
            # TODO delete patient`s avatar if it is exist

            users_client = SendbirdUsers(sendbird.app_id, sendbird.master_api_token)
            gchannels_client = SendbirdGroupChannels(sendbird.app_id, sendbird.master_api_token)

            await users_client.delete(user_id=db_object.cognito_sub)
            await gchannels_client.delete(channel_url=db_object.sendbird.feed_channel_url, )

        trx.commitAll()

    return db_object
