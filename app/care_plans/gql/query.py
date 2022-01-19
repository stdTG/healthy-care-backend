from typing import List

import graphene
from graphql import GraphQLError

import core.factory.gql as gql_factory
from core.errors import ErrorEnum
from .payloads import CarePlanAssignment
from ..models.care_plan_db import CarePlanAssignment as DbCpAssignment
from ..models.care_plan_db import DbCarePlan
from ..models.gql import GqlCarePlan, GqlCarePlanType

CarePlanPagedList, CarePlanPagedListField, PageInfo = gql_factory.create_paged_list(GqlCarePlan)
AssignmentPagedList, AssignmentPagedListField, _ = gql_factory.create_paged_list(CarePlanAssignment)


class CarePlanQueries(graphene.ObjectType):
    one = graphene.Field(GqlCarePlan, type_=graphene.Argument(GqlCarePlanType, name="type"),
                         id_=graphene.ID())
    list_ = CarePlanPagedListField(
        name="list",
        type_=graphene.Argument(GqlCarePlanType, name="type")
    )
    assignments = AssignmentPagedListField(
        patient_id=graphene.ID(name="patient"),
    )

    async def resolve_one(root, info, type_: GqlCarePlanType, id_):
        dbo: DbCarePlan = DbCarePlan.objects.with_id(id_)
        if dbo:
            return GqlCarePlan.from_db(dbo)

    async def resolve_list_(root, info, type_: GqlCarePlanType, page: int, per_page: int, ):
        if page < 0:
            raise GraphQLError(
                message="Argument `page` should be positive number.",
                extensions={"code": ErrorEnum.GRAPHQL_VALIDATION_FAILED},
            )
        if per_page <= 0:
            raise GraphQLError(
                message="Argument `pageSize` should be positive number.",
                extensions={"code": ErrorEnum.GRAPHQL_VALIDATION_FAILED},
            )
        query = DbCarePlan.objects()

        total_count = query.count()
        dbo_paged_list = query \
            .skip(page * per_page) \
            .limit(per_page) \
            .order_by('_id') \
            .all()

        result = CarePlanPagedList()

        result.items = [GqlCarePlan.from_db(dbo) for dbo in dbo_paged_list]
        result.page_info = PageInfo(
            page=page,
            per_page=per_page,
            total_items=total_count
        )

        return result

    async def resolve_assignments(root, info, page: int, per_page: int, patient_id):
        if page < 0:
            raise GraphQLError(
                message="Argument `page` should be positive number.",
                extensions={"code": ErrorEnum.GRAPHQL_VALIDATION_FAILED},
            )
        if per_page <= 0:
            raise GraphQLError(
                message="Argument `pageSize` should be positive number.",
                extensions={"code": ErrorEnum.GRAPHQL_VALIDATION_FAILED},
            )
        assgns: List[DbCpAssignment] = DbCpAssignment.objects(patient_id=patient_id).all()
        cps: List[DbCarePlan] = DbCarePlan.objects(
            id__in=[asgn.care_plan_id for asgn in assgns]).all()
        cps_dict = {cp.id: cp for cp in cps}

        total_count = len(assgns)
        result = AssignmentPagedList()

        items = []
        for assgn in assgns:
            item = CarePlanAssignment()
            item.care_plan = GqlCarePlan.from_db(cps_dict[assgn.care_plan_id])
            item.assigment_date_time = assgn.assigment_date_time
            item.execution_start_date_time = assgn.execution_start_date_time

            items.append(item)

        result.items = items
        result.page_info = PageInfo(
            page=page,
            per_page=per_page,
            total_items=total_count
        )

        return result
