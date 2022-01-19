import graphene

from app.context import get_current_auth, get_current_workspace
from app.models.db import WorkingHours as DbWorkingHours
from app.models.gql import AddWorkingHoursInput
from app.users.common.models.db import DashboardUser as DbDashboardUser
from app.users.common.models.gql import DashboardUser as GqlDashboardUser
from app.users.dashboard.logic.user import create_dashboard_user_handler
from core.errors import NotFoundGqlError, TitleAlreadyTakenGqlError, ValidationGqlError
from core.logic.base_payload import MutationPayload
from ..inputs import DashboardUserInput, DashboardUserUpdateInput, DashboardUserUpdateMeInput
from ..utils import is_email_exist, is_empty, is_phone_exist
from ...logic.user import delete_user_handler
from ...logic.user.update import update_dashboard_user_handler


class CreateDashboardUser(MutationPayload):
    """Mutation to create Dashboard user."""

    class Arguments:
        record = DashboardUserInput(required=True)

    result = graphene.Field(GqlDashboardUser)
    result_id = graphene.ID()

    async def mutate(self, info, record):

        # TODO check is authenticated and permission for create
        # if not info.context.user.is_authenticated:
        #    errors.append(NotAuthenticated(...))

        if not CreateDashboardUser._is_exist_contacts(record):
            error = ValidationGqlError(
                message="`byEmail.email` or `byPhone.phone` fields must not be empty")
            return CreateDashboardUser(error=error)

        if CreateDashboardUser._is_email_exist_in_db(record):
            error = TitleAlreadyTakenGqlError(message="Email already taken", path="byEmail.email")
            return CreateDashboardUser(error=error)

        if CreateDashboardUser._is_phone_exist_in_db(record):
            error = TitleAlreadyTakenGqlError(message="Phone already taken", path="byPhone.phone")
            return CreateDashboardUser(error=error)

        request = info.context["request"]
        current_workspace = await get_current_workspace(request)
        db_user = await create_dashboard_user_handler(record, current_workspace)

        return CreateDashboardUser(result_id=db_user.id, result=GqlDashboardUser.from_db(db_user))

    @staticmethod
    def _is_exist_contacts(record) -> bool:
        return bool(record.byEmail or record.byPhone)

    @staticmethod
    def _is_email_exist_in_db(record) -> bool:
        if not record.byEmail:
            return False
        else:
            return not is_empty(record.byEmail.email) and is_email_exist(
                email=record.byEmail.email, user_collection=DbDashboardUser
            )

    @staticmethod
    def _is_phone_exist_in_db(record) -> bool:
        if not record.byPhone:
            return False
        return not is_empty(record.byPhone.phone) and is_phone_exist(
            phone=record.byPhone.phone, user_collection=DbDashboardUser
        )


class UpdateDashboardUserMe(MutationPayload):
    """Mutation to update basic Dashboard user information."""

    class Arguments:
        record = DashboardUserUpdateMeInput(required=True)

    result_id = graphene.ID()
    result = graphene.Field(GqlDashboardUser)

    async def mutate(self, info, record: DashboardUserUpdateMeInput):
        # TODO check permission for update
        request = info.context["request"]
        current_auth = await get_current_auth(request)
        current_workspace = await get_current_workspace(request)

        db_user = DbDashboardUser.objects(cognito_sub=current_auth.sub).first()
        if not db_user:
            error = NotFoundGqlError(message="Dashboard-user is not found")
            return UpdateDashboardUser(error=error)

        db_user = update_dashboard_user_handler(db_user, record, current_workspace)
        return UpdateDashboardUser(result_id=db_user.id, result=GqlDashboardUser.from_db(db_user))


class UpdateDashboardUser(MutationPayload):
    """Mutation to update basic Dashboard user information."""

    class Arguments:
        user_id = graphene.ID(required=True, name="user")
        record = DashboardUserUpdateInput(required=True)

    result_id = graphene.ID()
    result = graphene.Field(GqlDashboardUser)

    async def mutate(self, info, record: DashboardUserUpdateInput, user_id: str):
        # TODO check permission for update
        request = info.context["request"]
        current_workspace = await get_current_workspace(request)

        db_user = DbDashboardUser.objects(deleted__ne=True, id=user_id).first()
        if not db_user:
            error = NotFoundGqlError(message="Dashboard-user is not found")
            return UpdateDashboardUser(error=error)

        db_user = update_dashboard_user_handler(db_user, record, current_workspace)
        return UpdateDashboardUser(result_id=db_user.id, result=GqlDashboardUser.from_db(db_user))


class AddHours(MutationPayload, graphene.Mutation):
    """Add working hours for Dashboard user."""

    class Arguments:
        record = AddWorkingHoursInput(required=True)

    result_id = graphene.ID()
    result = graphene.Field(GqlDashboardUser)

    async def mutate(self, info, record: AddWorkingHoursInput):
        # TODO check permission

        current_auth = info.context["request"].state.auth_claims

        weekdays = [wh.dayOfWeek for wh in record.working_hours]
        if len(weekdays) > len(set(weekdays)):
            error = ValidationGqlError(path="dayOfWeek", message="Days of week should be unique")
            return CreateDashboardUser(error=error)

        db_user = DbDashboardUser.objects(cognito_sub=current_auth.sub).first()
        if not db_user:
            error = NotFoundGqlError(message="Dashboard-user is not found")
            return UpdateDashboardUser(error=error)

        db_user.workingHours = [DbWorkingHours.from_gql(wh) for wh in record.working_hours]
        db_user.save()

        return UpdateDashboardUser(result_id=db_user.id, result=GqlDashboardUser.from_db(db_user))


class DeleteUser(MutationPayload):
    """Mutation to delete user by id."""

    class Arguments:
        id_ = graphene.ID(required=True)

    async def mutate(self, info, id_):
        await delete_user_handler(id_, info.context["request"])

        return DeleteUser()


class DashboardUserMutations(graphene.Mutation):
    create = CreateDashboardUser.Field()
    delete = DeleteUser.Field()
    update = UpdateDashboardUser.Field()
    update_me = UpdateDashboardUserMe.Field()
    add_hours_me = AddHours.Field()

    async def mutate(self, _):
        return {}
