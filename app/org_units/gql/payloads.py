import graphene

from app.users.common.models.gql import DashboardUser
from core.logic.base_payload import PaginationInfo
from ..model_gql import CareTeam as GqlCareTeam, SubOrganization as GqlSubOrg


class CareTeamPagination(graphene.ObjectType):
    items = graphene.List(GqlCareTeam, required=True)
    page_info = graphene.Field(PaginationInfo, required=True)


class SubOrgPagination(graphene.ObjectType):
    items = graphene.List(GqlSubOrg, required=True)
    page_info = graphene.Field(PaginationInfo, required=True)


class UserPagination(graphene.ObjectType):
    items = graphene.List(DashboardUser, required=True)
    page_info = graphene.Field(PaginationInfo, required=True)


class OrgUnit(graphene.Union):
    class Meta:
        types = (GqlSubOrg, GqlCareTeam,)
