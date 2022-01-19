import graphene

from core.factory.gql import create_paged_list
from core.logic.base_payload import PaginationInfo
from ..models.db import MedicalCondition as DbMedCond
from ..models.gql import MedicalCondition as GqlMedCond

MedConditionPagedList, MedConditionPagedListField, PageInfo = create_paged_list(GqlMedCond)


class MedicalConditionQueries(graphene.ObjectType):
    get_by_index = graphene.Field(GqlMedCond, id_=graphene.ID(required=True))
    pagination = MedConditionPagedListField()

    async def resolve_get_by_id(self, _, id_):
        med_cond = DbMedCond.objects.with_id(id_)

        if med_cond:
            return GqlMedCond.from_db(med_cond)

    async def resolve_pagination(self, _, page: int, per_page: int):
        queryset = DbMedCond.objects()

        count = queryset.count()
        med_conditions = (queryset
                          .skip(page * per_page)
                          .limit(per_page)
                          .all())

        pagination = MedConditionPagedList()
        pagination.page_info = PaginationInfo(page=page, per_page=per_page, total_items=count)
        pagination.items = [GqlMedCond.from_db(md) for md in med_conditions]

        return pagination
