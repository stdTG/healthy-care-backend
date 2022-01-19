import graphene

from app.booking.models.db import Appointment
from app.context import get_current_master_org, get_current_workspace
from app.models.db import Address, WorkingHours as DbWorkingHours
from app.models.gql import AddWorkingHoursInput
from app.users.common.models.db import DashboardUser as DbDashboardUser, PatientUser as Patient
from core.errors import NotFoundGqlError, TitleAlreadyTakenGqlError, ValidationGqlError
from core.logic.base_payload import MutationPayload
from .inputs import (AddUserToOrgUnitInput, AddWorkingHoursToSubOrgInput, CareTeamCreateInput,
                     CareTeamUpdateInput,
                     MasterOrgUpdateInput,
                     SubOrgCreateInput, SubOrgUpdateInput)
from .payloads import OrgUnit as GqlOrgUnit
from ..logic.dashboard.care_team import update_care_team_handler
from ..logic.dashboard.sub_org import update_sub_org_handler
from ..model_db import OrgUnit as DbOrgUnit
from ..model_gql import CareTeam as GqlCareTeam, MasterOrganization, SubOrganization as GqlSubOrg


# TODO check name of masterorg is unique

class CreateSubOrg(MutationPayload):
    """Mutation to create suborganization."""

    class Arguments:
        record = SubOrgCreateInput(required=True)

    result = graphene.Field(GqlSubOrg)
    result_id = graphene.ID()

    async def mutate(self, _, record: SubOrgCreateInput):
        # TODO check is authenticated and permission for create
        if CreateSubOrg.is_exist(record.name):
            error = TitleAlreadyTakenGqlError(message="Sub_org with name already taken",
                                              path="name")
            return CreateSubOrg(error=error)

        db_sub_org = DbOrgUnit.from_gql_sub_org(record)
        db_sub_org.save()

        if record.users:
            DbDashboardUser.objects(pk__in=record.users).update(set__orgUnitId=db_sub_org.id)
        if record.care_teams:
            DbOrgUnit.objects(pk__in=record.care_teams).update(set__parentId=db_sub_org.id)

        return CreateSubOrg(result_id=db_sub_org.id, result=GqlSubOrg.from_db(db_sub_org))

    @staticmethod
    def is_exist(name) -> bool:
        return DbOrgUnit.objects(name=name).first()


class CreateCareTeam(MutationPayload):
    """Mutation to create care team.
    """

    class Arguments:
        record = CareTeamCreateInput(required=True)

    result = graphene.Field(GqlCareTeam)
    result_id = graphene.ID()

    async def mutate(self, _, record: CareTeamCreateInput):
        if record.sub_org_id and not CreateCareTeam._is_exist_parent(record.sub_org_id):
            error = ValidationGqlError(message="Suborganization with id does not exist",
                                       path="subOrgId")
            return CreateSubOrg(error=error)

        db_care_team = DbOrgUnit.from_gql_care_team(record)
        db_care_team.save()

        if record.users:
            DbDashboardUser.objects(pk__in=record.users).update(set__orgUnitId=db_care_team.id)
        return CreateSubOrg(result_id=db_care_team.id, result=GqlCareTeam.from_db(db_care_team))

    @staticmethod
    def _is_exist_parent(parent_id: str) -> bool:
        return DbOrgUnit.objects.filter(pk=parent_id, isCareTeam=False).first()


class ConfirmWorkingHours(MutationPayload):
    """Confirm default working hours for master organization.
    """

    result = graphene.Field(MasterOrganization)

    async def mutate(self, info):
        request = info.context["request"]
        master_org = await get_current_master_org(request)
        master_org.isDefaultWorkingHours = True
        master_org.save()

        return ConfirmWorkingHours(record=MasterOrganization.from_db(master_org))


class DeleteCareTeam(MutationPayload):
    """Mutation to delete patient by id."""

    class Arguments:
        id_ = graphene.ID(required=True)

    async def mutate(self, _, id_):
        care_team = DbOrgUnit.objects.with_id(id_)
        is_deleted = DbOrgUnit.objects(pk=id_, isCareTeam=True).delete()
        if is_deleted:
            DbDashboardUser.objects(orgUnitId=id_).update(set__orgUnitId=care_team.parentId)
            Patient.objects(orgUnitId=id_).update(set__orgUnitId=None)
        return DeleteCareTeam()


class DeleteSubOrg(MutationPayload):
    """Mutation to delete patient by id."""

    class Arguments:
        id_ = graphene.ID(required=True)

    async def mutate(self, _, id_):
        is_deleted = DbOrgUnit.objects(pk=id_, isCareTeam=False, ).delete()
        if is_deleted:
            DbDashboardUser.objects(orgUnitId=id_).update(set__orgUnitId=None)
            Patient.objects(orgUnitId=id_).update(set__orgUnitId=None)
            DbOrgUnit.objects(parentId=id_).update(set__parentId=None)
            Appointment.objects(location=id_).update(set__location=None)
        return DeleteSubOrg()


class UpdateSubOrg(MutationPayload):
    """Mutation to update sub organization information."""

    class Arguments:
        record = SubOrgUpdateInput(required=True)

    result_id = graphene.ID()
    result = graphene.Field(GqlSubOrg)

    async def mutate(self, info, record: SubOrgUpdateInput):
        if not record.name:
            error = ValidationGqlError(message="Field `name` should not be empty.", path="name")
            return UpdateSubOrg(error=error)

        request = info.context["request"]
        workspace = await get_current_workspace(request)
        org_unit = DbOrgUnit.objects(pk=record.id_, isCareTeam=False,
                                     name__ne=workspace.human_friendly_name).first()
        if not org_unit:
            error = NotFoundGqlError(message="Suborganization with id does not exist")
            return UpdateSubOrg(error=error)

        update_sub_org_handler(org_unit, record, )

        return UpdateSubOrg(result_id=org_unit.id, result=GqlSubOrg.from_db(org_unit))


class UpdateMasterOrg(MutationPayload):
    """Mutation to update master organization information."""

    class Arguments:
        record = MasterOrgUpdateInput(required=True)

    result = graphene.Field(GqlSubOrg)

    async def mutate(self, info, record: MasterOrgUpdateInput):
        if not record.name:
            error = ValidationGqlError(message="Field `name` should not be empty.", path="name")
            return UpdateMasterOrg(error=error)

        request = info.context["request"]

        workspace = await get_current_workspace(request)
        master_org = await get_current_master_org(request)

        UpdateMasterOrg.update(master_org, record)

        if record.name != workspace.human_friendly_name:
            workspace.human_friendly_name = record.name
            workspace.save()

        return UpdateMasterOrg(result=MasterOrganization.from_db(master_org))

    @staticmethod
    def update(master_org: DbOrgUnit, record: MasterOrgUpdateInput):
        master_org.name = record.name
        master_org.email = record.email
        master_org.phone = record.phone
        master_org.site = record.site
        master_org.address = Address.from_gql(
            record.full_address) if record.full_address else Address()
        master_org.language = record.language
        master_org.facebook = record.facebook
        master_org.linkedin = record.linkedin
        master_org.instagram = record.instagram
        master_org.description = record.description
        master_org.save()


class UpdateCareTeam(MutationPayload):
    """Mutation to update care team information."""

    class Arguments:
        record = CareTeamUpdateInput(required=True)

    result_id = graphene.ID()
    result = graphene.Field(GqlCareTeam)

    async def mutate(self, _, record: CareTeamUpdateInput):
        if not record.name:
            error = ValidationGqlError(message="Field `name` should not be empty.", path="name")
            return UpdateCareTeam(error=error)

        care_team = DbOrgUnit.objects(pk=record.id_, isCareTeam=True).first()
        if not care_team:
            error = NotFoundGqlError(message=f"CareTeam with id `{record.id_}` does not exist")
            return UpdateCareTeam(error=error)

        update_care_team_handler(care_team, record)

        return UpdateCareTeam(result_id=care_team.id, result=GqlCareTeam.from_db(care_team))


class AddHoursToSubOrg(MutationPayload):
    """Add working hours to sub organization."""

    class Arguments:
        record = AddWorkingHoursToSubOrgInput(required=True)

    result_id = graphene.ID()
    result = graphene.Field(GqlSubOrg)

    async def mutate(self, _, record: AddWorkingHoursToSubOrgInput):
        weekdays = [wh.dayOfWeek for wh in record.working_hours]
        if len(weekdays) > len(set(weekdays)):
            error = ValidationGqlError(path="dayOfWeek", message="Days of week should be unique")
            return AddHoursToSubOrg(error=error)

        sub_org = DbOrgUnit.objects(pk=record.sub_org, isCareTeam=False).first()
        if not sub_org:
            error = NotFoundGqlError(message="Sub organization is not found")
            return AddHoursToSubOrg(error=error)

        sub_org.workingHours = [DbWorkingHours.from_gql(wh) for wh in record.working_hours]
        sub_org.save()

        return AddHoursToSubOrg(result_id=sub_org.id, result=GqlSubOrg.from_db(sub_org))


class AddHoursToMasterOrg(MutationPayload):
    """Add working hours to master organization."""

    class Arguments:
        record = AddWorkingHoursInput(required=True)

    result = graphene.Field(MasterOrganization)

    async def mutate(self, info, record: AddWorkingHoursInput):
        weekdays = [wh.dayOfWeek for wh in record.working_hours]
        if len(weekdays) > len(set(weekdays)):
            error = ValidationGqlError(path="dayOfWeek", message="Days of week should be unique")
            return AddHoursToSubOrg(error=error)

        request = info.context["request"]
        master_org = await get_current_master_org(request)
        master_org.workingHours = [DbWorkingHours.from_gql(wh) for wh in record.working_hours]
        master_org.isDefaultWorkingHours = False
        master_org.save()

        return AddHoursToSubOrg(record=MasterOrganization.from_db(master_org))


class AddUserToOrgUnit(MutationPayload):
    """Add user to care-team or sub-organization."""

    class Arguments:
        record = AddUserToOrgUnitInput(required=True)

    result_id = graphene.ID()
    result = graphene.Field(GqlOrgUnit)

    async def mutate(self, info, record: AddUserToOrgUnitInput):
        request = info.context["request"]
        workspace = await get_current_workspace(request)
        org_unit = DbOrgUnit.objects(pk=record.org_unit).first()

        if not org_unit or org_unit.name == workspace.human_friendly_name:
            return AddUserToOrgUnit(error=NotFoundGqlError())

        DbDashboardUser.objects(pk__in=record.users).update(set__orgUnitId=org_unit.id)
        if org_unit.isCareTeam:
            return AddUserToOrgUnit(result_id=org_unit.id, result=GqlCareTeam.from_db(org_unit))
        else:
            return AddUserToOrgUnit(result_id=org_unit.id, result=GqlSubOrg.from_db(org_unit))


class DeleteUserFromOrgUnit(MutationPayload):
    """Delete user from care-team or sub-organization."""

    class Arguments:
        record = AddUserToOrgUnitInput(required=True)

    result_id = graphene.ID()
    result = graphene.Field(GqlOrgUnit)

    async def mutate(self, info, record: AddUserToOrgUnitInput):
        request = info.context["request"]
        workspace = await get_current_workspace(request)
        org_unit = DbOrgUnit.objects(pk=record.org_unit).first()

        if not org_unit or org_unit.name == workspace.human_friendly_name:
            return AddUserToOrgUnit(error=NotFoundGqlError())

        DbDashboardUser.objects(pk__in=record.users).update(set__orgUnitId=org_unit.parentId)
        if org_unit.isCareTeam:
            return AddUserToOrgUnit(result_id=org_unit.id, result=GqlCareTeam.from_db(org_unit))
        else:
            return AddUserToOrgUnit(result_id=org_unit.id, result=GqlSubOrg.from_db(org_unit))


class OrgUnitMutations(graphene.Mutation):
    create_sub_org = CreateSubOrg.Field()
    create_care_team = CreateCareTeam.Field()
    add_hours_to_sub_org = AddHoursToSubOrg.Field()
    add_hours_to_master_org = AddHoursToMasterOrg.Field()
    add_users = AddUserToOrgUnit.Field()

    delete_care_team = DeleteCareTeam.Field()
    delete_sub_org = DeleteSubOrg.Field()
    delete_users = DeleteUserFromOrgUnit.Field()

    confirm_working_hours = ConfirmWorkingHours.Field()
    update_sub_org = UpdateSubOrg.Field()
    update_care_team = UpdateCareTeam.Field()
    update_master_org = UpdateMasterOrg.Field()

    async def mutate(self, _):
        return {}
