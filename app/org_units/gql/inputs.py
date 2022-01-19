import graphene

from app.models.gql import AddWorkingHoursInput, AddressInput
from core.gql.types import GrapheneMongoId


class SubOrgCreateInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String()
    phone = graphene.String()
    full_address = graphene.Field(AddressInput)
    supervisors = graphene.List(graphene.NonNull(GrapheneMongoId))
    users = graphene.List(graphene.NonNull(GrapheneMongoId))
    care_teams = graphene.List(graphene.NonNull(GrapheneMongoId))
    site = graphene.String()


class CareTeamCreateInput(graphene.InputObjectType):
    sub_org_id = GrapheneMongoId()
    supervisors = graphene.List(graphene.NonNull(GrapheneMongoId))
    users = graphene.List(graphene.NonNull(GrapheneMongoId))
    name = graphene.String(required=True)


class SubOrgUpdateInput(graphene.InputObjectType):
    id_ = GrapheneMongoId(required=True)
    name = graphene.String(required=True)
    email = graphene.String()
    phone = graphene.String()
    full_address = graphene.Field(AddressInput)
    supervisors = graphene.List(graphene.NonNull(GrapheneMongoId))
    user_ids = graphene.List(graphene.NonNull(GrapheneMongoId), name="users")
    care_team_ids = graphene.List(graphene.NonNull(GrapheneMongoId), name="careTeams")
    site = graphene.String()


class MasterOrgUpdateInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String()
    phone = graphene.String()
    full_address = graphene.Field(AddressInput)
    site = graphene.String()
    language = graphene.String()
    facebook = graphene.String()
    linkedin = graphene.String()
    instagram = graphene.String()
    description = graphene.String()


class CareTeamUpdateInput(graphene.InputObjectType):
    id_ = GrapheneMongoId(required=True)
    name = graphene.String(required=True)
    sub_org_id = GrapheneMongoId()
    supervisors = graphene.List(graphene.NonNull(GrapheneMongoId))
    users = graphene.List(graphene.NonNull(GrapheneMongoId))


class AddUserToOrgUnitInput(graphene.InputObjectType):
    org_unit = GrapheneMongoId(required=True)
    users = graphene.List(graphene.NonNull(GrapheneMongoId))


class AddWorkingHoursToSubOrgInput(AddWorkingHoursInput):
    sub_org = GrapheneMongoId(required=True)


class FilterFindManyOrgUnit(graphene.InputObjectType):
    name = graphene.String()


class FilterFindManyUser(graphene.InputObjectType):
    name = graphene.String()


class FilterFindManyCareTeam(graphene.InputObjectType):
    name = graphene.String()
    is_free = graphene.Boolean()
