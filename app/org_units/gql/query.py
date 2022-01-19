import re

import graphene
from graphql import GraphQLError

from app.context import get_current_master_org, get_current_workspace
from app.users.common.models.db import DashboardUser as DbDashboardUser
from app.users.common.models.gql import DashboardUser as GqlDashboardUser
from core.errors import ErrorEnum
from core.logic.base_payload import PaginationInfo
from .inputs import FilterFindManyCareTeam, FilterFindManyOrgUnit, FilterFindManyUser
from .payloads import CareTeamPagination, SubOrgPagination, UserPagination
from ..model_db import OrgUnit as DbOrgUnit
from ..model_gql import CareTeam as GqlCareTeam, MasterOrganization, SubOrganization as GqlSubOrg
from ...users.dashboard.logic.user.search import search_users


class OrgUnitQueries(graphene.ObjectType):
    sub_org_by_id = graphene.Field(GqlSubOrg, id_=graphene.ID(required=True))
    sub_org_pagination = graphene.Field(
        type=SubOrgPagination,
        page=graphene.Int(required=True),
        per_page=graphene.Int(required=True, default_value=10),
        filter_=FilterFindManyOrgUnit(required=False, name="filter"),
    )
    sub_org_user_pagination = graphene.Field(
        type=UserPagination,
        page=graphene.Int(required=True),
        per_page=graphene.Int(required=True, default_value=10),
        sub_org_id=graphene.ID(required=True),
        filter=FilterFindManyUser(),
    )

    care_team_by_id = graphene.Field(GqlCareTeam, id_=graphene.ID(required=True))
    care_team_pagination = graphene.Field(
        type=CareTeamPagination,
        page=graphene.Int(required=True),
        per_page=graphene.Int(required=True, default_value=10),
        filter_=FilterFindManyCareTeam(required=False, name="filter"),
    )
    care_team_user_pagination = graphene.Field(
        type=UserPagination,
        page=graphene.Int(required=True),
        per_page=graphene.Int(required=True, default_value=10),
        care_team_id=graphene.ID(required=True),
        filter=FilterFindManyUser()
    )

    master_org_me = graphene.Field(MasterOrganization)

    async def resolve_sub_org_by_id(self, info, id_):
        request = info.context["request"]
        workspace = await get_current_workspace(request)

        sub_org = DbOrgUnit.objects(pk=id_, name__ne=workspace.human_friendly_name).first()

        if sub_org:
            return GqlSubOrg.from_db(sub_org)

    async def resolve_sub_org_pagination(self, info, page: int, per_page: int, **kwargs):
        if page < 0:
            raise GraphQLError(
                message="Argument `page` should be positive number.",
                extensions={"code": ErrorEnum.GRAPHQL_VALIDATION_FAILED},
            )
        if per_page <= 0:
            raise GraphQLError(
                message="Argument `perPage` should be positive number.",
                extensions={"code": ErrorEnum.GRAPHQL_VALIDATION_FAILED},
            )

        request = info.context["request"]
        workspace = await get_current_workspace(request)
        sub_org_queryset = DbOrgUnit.objects(isCareTeam=False,
                                             name__ne=workspace.human_friendly_name)

        if "filter_" in kwargs:
            filter_: FilterFindManyOrgUnit = kwargs["filter_"]
            if filter_.name:
                sub_org_queryset = sub_org_queryset.filter(name=create_regexp(filter_.name))

        sub_org_count = sub_org_queryset.count()
        sub_orgs = sub_org_queryset \
            .skip(page * per_page) \
            .limit(per_page) \
            .all()

        pagination = SubOrgPagination()
        pagination_info = PaginationInfo(page=page, per_page=per_page, total_items=sub_org_count)
        pagination.page_info = pagination_info
        pagination.items = [GqlSubOrg.from_db(sub_org) for sub_org in sub_orgs]

        return pagination

    async def resolve_care_team_by_id(self, _, id_):
        care_team: DbOrgUnit = DbOrgUnit.objects(pk=id_).first()

        if care_team and care_team.isCareTeam:
            return GqlCareTeam.from_db(care_team)

    async def resolve_care_team_pagination(self, _, page: int, per_page: int, **kwargs):
        if page < 0:
            raise GraphQLError(
                message="Argument `page` should be positive number.",
                extensions={"code": ErrorEnum.GRAPHQL_VALIDATION_FAILED},
            )
        if per_page <= 0:
            raise GraphQLError(
                message="Argument `perPage` should be positive number.",
                extensions={"code": ErrorEnum.GRAPHQL_VALIDATION_FAILED},
            )

        care_team_queryset = DbOrgUnit.objects(isCareTeam=True)

        if "filter_" in kwargs:
            filter_: FilterFindManyCareTeam = kwargs["filter_"]
            if filter_.name:
                care_team_queryset = care_team_queryset.filter(name=create_regexp(filter_.name))

        care_team_count = care_team_queryset.count()
        care_teams = care_team_queryset \
            .skip(page * per_page) \
            .limit(per_page) \
            .all()

        pagination = SubOrgPagination()
        pagination_info = PaginationInfo(page=page, per_page=per_page, total_items=care_team_count)

        mapped_care_teams = []
        if "filter_" in kwargs:
            filter_: FilterFindManyCareTeam = kwargs["filter_"]
            if filter_.is_free:
                mapped_care_teams = [GqlCareTeam.from_db(care_team) for care_team in care_teams if
                                     not care_team.parentId]
            elif filter_.is_free is False:
                mapped_care_teams = [GqlCareTeam.from_db(care_team) for care_team in care_teams if
                                     care_team.parentId]
        if not mapped_care_teams:
            mapped_care_teams = [GqlCareTeam.from_db(care_team) for care_team in care_teams]

        pagination.page_info = pagination_info
        pagination.items = mapped_care_teams

        return pagination

    async def resolve_sub_org_user_pagination(self, info, page: int, per_page: int, **kwargs):
        if page < 0:
            raise GraphQLError(
                message="Argument `page` should be positive number.",
                extensions={"code": ErrorEnum.GRAPHQL_VALIDATION_FAILED},
            )
        if per_page <= 0:
            raise GraphQLError(
                message="Argument `perPage` should be positive number.",
                extensions={"code": ErrorEnum.GRAPHQL_VALIDATION_FAILED},
            )

        sub_org_id = kwargs.get("sub_org_id")
        sub_org: DbOrgUnit = DbOrgUnit.objects(pk=sub_org_id, isCareTeam=False, )

        if not sub_org:
            raise GraphQLError(
                message=f"sub organization with `subOrgId` {sub_org_id} not found",
                extensions={"code": ErrorEnum.NOT_FOUND},
            )

        care_teams = DbOrgUnit.objects(parentId=sub_org_id).all()
        ids = [cm.id for cm in care_teams]
        ids.append(sub_org_id)

        users_queryset = DbDashboardUser.objects(orgUnitId__in=ids, deleted__ne=True)
        if "filter" in kwargs:
            filter_: FilterFindManyUser = kwargs["filter"]
            if filter_.name:
                users_queryset = search_users(filter_.name, users_queryset)

        users_count = users_queryset.count()
        users = users_queryset.skip(page * per_page).limit(per_page).all()

        pagination = UserPagination()
        pagination_info = PaginationInfo(page=page, per_page=per_page, total_items=users_count)
        pagination.page_info = pagination_info
        pagination.items = [GqlDashboardUser.from_db(user) for user in users]

        return pagination

    async def resolve_care_team_user_pagination(self, _, page: int, per_page: int, **kwargs):
        if page < 0:
            raise GraphQLError(
                message="Argument `page` should be positive number.",
                extensions={"code": ErrorEnum.GRAPHQL_VALIDATION_FAILED},
            )
        if per_page <= 0:
            raise GraphQLError(
                message="Argument `perPage` should be positive number.",
                extensions={"code": ErrorEnum.GRAPHQL_VALIDATION_FAILED},
            )

        care_team_id = kwargs.get("care_team_id")
        care_team: DbOrgUnit = DbOrgUnit.objects(pk=care_team_id, isCareTeam=True, )
        if not care_team:
            raise GraphQLError(
                message=f"care team with `careTeamId` {care_team} not found",
                extensions={"code": ErrorEnum.NOT_FOUND},
            )

        users_queryset = DbDashboardUser.objects(orgUnitId=care_team_id, deleted__ne=True)

        if "filter" in kwargs:
            filter_: FilterFindManyUser = kwargs["filter"]
            if filter_.name:
                users_queryset = search_users(filter_.name, users_queryset)

        users_count = users_queryset.count()
        users = users_queryset.skip(page * per_page).limit(per_page).all()

        pagination = UserPagination()
        pagination_info = PaginationInfo(page=page, per_page=per_page, total_items=users_count)
        pagination.page_info = pagination_info
        pagination.items = [GqlDashboardUser.from_db(user) for user in users]

        return pagination

    async def resolve_master_org_me(self, info):
        request = info.context["request"]
        master_org = await get_current_master_org(request)
        return MasterOrganization.from_db(master_org)


def create_regexp(str_: str):
    str_ = str_.lower()
    return re.compile(f".*{str_}.*", re.IGNORECASE)
