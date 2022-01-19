from __future__ import annotations

from typing import TYPE_CHECKING, Union

from mongoengine.fields import ObjectId

from app.models.db import Address
from app.users.dashboard.gql.utils import get_user_name
from core.cognito import CognitoUsers

if TYPE_CHECKING:

    from app.tenant_workspaces.model_db import Workspace
    from app.users.common.models.db import DashboardUser as DbUser

from app.users.dashboard.gql.inputs import DashboardUserUpdateMeInput, DashboardUserUpdateInput


def update_dashboard_user_handler(user_db: DbUser,
                                  record: Union[
                                      DashboardUserUpdateMeInput, DashboardUserUpdateInput],
                                  workspace: Workspace, ):
    if record.firstName:
        user_db.firstName = record.firstName
    if record.lastName:
        user_db.lastName = record.lastName

    if isinstance(record, DashboardUserUpdateMeInput):
        update_me(user_db, record)

    if isinstance(record, DashboardUserUpdateInput):
        if record.role and record.role != user_db.role:
            cognito_users = CognitoUsers(aws_region=workspace.aws_region)
            username = get_user_name(user_db.email, user_db.phone)

            cognito_users.delete_from_group(workspace.cognito.user_pool_id, username, user_db.role)
            cognito_users.add_to_group(workspace.cognito.user_pool_id, username, record.role)

        user_db.role = record.role

        if record.org_unit:
            user_db.orgUnitId = ObjectId(record.org_unit)
        else:
            user_db.orgUnitId = None

    user_db.save()

    return user_db


def update_me(user_db: DbUser, record: DashboardUserUpdateMeInput):
    if record.status:
        user_db.status = record.status

    if record.description:
        user_db.description = record.description

    if record.language:
        user_db.language = record.language

    if record.sex:
        user_db.sex = record.sex

    if record.birthDate:
        user_db.birthDate = record.birthDate
    if record.title:
        user_db.title = record.title
    if record.speciality:
        user_db.speciality = record.speciality

    if record.address:
        user_db.address = Address.from_gql(record.address)
