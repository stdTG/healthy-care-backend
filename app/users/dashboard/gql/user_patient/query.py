from datetime import date

import graphene
from graphql import GraphQLError

from app.org_units.model_db import OrgUnit
from app.users.common.models.db import PatientUser as DbPatientUser
from app.users.common.models.gql import PatientUser as GqlPatientUser
from core.errors import ErrorEnum
from core.logic.base_payload import PaginationInfo
from ..inputs import FilterFindManyPatientInput
from ..payloads import PatientUserPagination
from ..utils import create_regexp


class PatientUserQueries(graphene.ObjectType):
    one = graphene.Field(GqlPatientUser, id_=graphene.ID())

    paged_list = graphene.Field(
        type=PatientUserPagination,
        filter_=FilterFindManyPatientInput(required=False, name="filter"),
        page=graphene.Int(required=True),
        per_page=graphene.Int(required=True, default_value=10)
    )

    async def resolve_one(self, _, id_):
        user = DbPatientUser.objects(pk=id_, deleted__ne=True).first()
        if not user:
            return None
        else:
            return GqlPatientUser.from_db(user)

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

        patients_queryset = DbPatientUser.objects(deleted__ne=True)
        if "filter_" in kwargs:
            filter_: FilterFindManyPatientInput = kwargs["filter_"]
            current = date.today()

            if filter_.name:
                patients_queryset = patients_queryset.search_text(filter_.name)

            if filter_.start_age is not None:
                start_date = current.replace(year=current.year - filter_.end_age)
                patients_queryset = patients_queryset.filter(birthDate__gte=start_date)

            if filter_.end_age:
                end_date = current.replace(year=current.year - filter_.start_age)
                patients_queryset = patients_queryset.filter(birthDate__lte=end_date)

            if filter_.care_team_id:
                patients_queryset = patients_queryset.filter(orgUnitId=filter_.care_team_id)

            elif filter_.sub_org_id:
                care_teams = OrgUnit.objects(parentId=filter_.sub_org_id).all()
                org_unit_ids = [cm.id for cm in care_teams]
                org_unit_ids.append(filter_.sub_org_id)

                patients_queryset = patients_queryset.filter(orgUnitId__in=org_unit_ids)

            if filter_.gender:
                patients_queryset = patients_queryset.filter(sex__in=filter_.gender)

            if filter_.location and filter_.location.isnumeric():
                patients_queryset = patients_queryset.filter(address__zipcode=filter_.location)
            elif filter_.location:
                patients_queryset = patients_queryset.filter(
                    address__city=create_regexp(filter_.location))

            if filter_.email:
                name_regex = create_regexp(filter_.email)
                patients_queryset = patients_queryset.filter(
                    email=name_regex
                )

            if filter_.medical_condition_index:
                patients_queryset = patients_queryset.filter(
                    medical_conditions__index=filter_.medical_condition_index
                )

        patients_count = patients_queryset.count()
        patients = patients_queryset \
            .skip(page * per_page) \
            .limit(per_page) \
            .all()

        pagination = PatientUserPagination()
        pagination_info = PaginationInfo(page=page, per_page=per_page, total_items=patients_count)
        pagination.page_info = pagination_info
        pagination.items = [GqlPatientUser.from_db(user) for user in patients]

        return pagination
