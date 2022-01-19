import graphene

from core.logic.base_payload import PaginationInfo
from .payloads import MedHistoryPagination
from ..models.db import MedicalHistory as DbMedCond
from ..models.gql import MedicalHistory as GqlMedCond


class MedicalHistoryQueries(graphene.ObjectType):
    get_by_id = graphene.Field(GqlMedCond, id_=graphene.ID(required=True))
    pagination = graphene.Field(
        type=MedHistoryPagination,
        page=graphene.Int(default_value=0),
        per_page=graphene.Int(default_value=10),
        patient_id=graphene.ID(required=True, name="patient")
    )

    async def resolve_get_by_id(self, info, id_):
        note = DbMedCond.objects.with_id(id_)

        if note:
            return GqlMedCond.from_db(note)

    async def resolve_pagination(self, info, page: int, per_page: int, patient_id):
        notes_queryset = DbMedCond.objects(patientId=patient_id)

        notes_count = notes_queryset.count()
        notes = (notes_queryset
                 .skip(page * per_page)
                 .limit(per_page)
                 .order_by("-date")
                 .all())

        pagination = MedHistoryPagination()
        pagination.page_info = PaginationInfo(page=page, per_page=per_page, total_items=notes_count)
        pagination.items = [GqlMedCond.from_db(note) for note in notes]

        return pagination
