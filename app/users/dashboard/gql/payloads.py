import graphene

from app.users.common.models.gql import DashboardUser as DashboardUser, PatientUser as PatientUser
from core.logic.base_payload import PaginationInfo


class PatientUserPagination(graphene.ObjectType):
    items = graphene.List(PatientUser, required=True)
    page_info = graphene.Field(PaginationInfo, required=True)


class DashboardUserPagination(graphene.ObjectType):
    items = graphene.List(DashboardUser, required=True)
    page_info = graphene.Field(PaginationInfo, required=True)


class DashboardUserList(graphene.ObjectType):
    items = graphene.List(DashboardUser, required=True)


class PatientUserList(graphene.ObjectType):
    items = graphene.List(PatientUser, required=True)
