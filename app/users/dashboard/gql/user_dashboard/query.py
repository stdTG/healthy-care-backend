import graphene
from graphql import GraphQLError

from app.org_units.model_db import OrgUnit
from app.users.common.models.db import DashboardUser as DbDashboardUser
from app.users.common.models.gql import DashboardUser as GqlDashboardUser
from core.errors import ErrorEnum
from core.logic.base_payload import PaginationInfo
from ..inputs import FilterFindManyUserInput
from ..payloads import DashboardUserPagination
from ...logic.user.search import search_users
from ...logic.utils import create_regexp


class DashboardUserQueries(graphene.ObjectType):
    me = graphene.Field(GqlDashboardUser)

    paged_list = graphene.Field(
        DashboardUserPagination,
        page=graphene.Int(required=True),
        per_page=graphene.Int(required=True, default_value=10),
        filter_=FilterFindManyUserInput(required=False, name="filter"),
    )

    async def resolve_me(self, info):
        current_auth = info.context["request"].state.auth_claims

        user = DbDashboardUser.objects(cognito_sub=current_auth.sub).first()
        if not user:
            return None
        else:
            return GqlDashboardUser.from_db(user)

    async def resolve_paged_list(self, _, page: int, per_page: int, **kwargs):
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

        users_queryset = DbDashboardUser.objects(deleted__ne=True)
        if "filter_" in kwargs:
            filter_: FilterFindManyUserInput = kwargs["filter_"]

            if filter_.role:
                users_queryset = users_queryset.filter(role=filter_.role)

            if filter_.care_team_id:
                users_queryset = users_queryset.filter(orgUnitId=filter_.care_team_id)
            elif filter_.sub_org_id:
                care_teams = OrgUnit.objects(parentId=filter_.sub_org_id).all()
                org_unit_ids = [ct.id for ct in care_teams]
                org_unit_ids.append(filter_.sub_org_id)

                users_queryset = users_queryset.filter(orgUnitId__in=org_unit_ids)

            if filter_.name:
                users_queryset = search_users(filter_.name, users_queryset)
            if filter_.email:
                name_regex = create_regexp(filter_.email)
                users_queryset = users_queryset.filter(
                    email=name_regex
                )

        users_count = users_queryset.count()
        users = users_queryset.skip(page * per_page).limit(per_page).all()

        pagination = DashboardUserPagination()
        pagination_info = PaginationInfo(page=page, per_page=per_page, total_items=users_count)
        pagination.page_info = pagination_info

        mapped_users = []
        if "filter_" in kwargs:
            filter_: FilterFindManyUserInput = kwargs["filter_"]
            if filter_.is_free:
                mapped_users = [GqlDashboardUser.from_db(user) for user in users if
                                not user.orgUnitId]
            elif filter_.is_free is False:
                mapped_users = [GqlDashboardUser.from_db(user) for user in users if user.orgUnitId]
        if not mapped_users:
            mapped_users = [GqlDashboardUser.from_db(user) for user in users]

        pagination.items = mapped_users

        return pagination
