import graphene

from core.logic.base_payload import PaginationInfo
from .payloads import NotePagination
from ..models.db import Note as DbNote
from ..models.gql import Note as GqlNote


class NoteQueries(graphene.ObjectType):
    get_by_id = graphene.Field(GqlNote, id_=graphene.ID(required=True))
    pagination = graphene.Field(
        type=NotePagination,
        page=graphene.Int(default_value=0),
        per_page=graphene.Int(default_value=10),
        patient_id=graphene.ID(name="patient", required=True),
    )

    async def resolve_get_by_id(self, info, id_):
        note = DbNote.objects.with_id(id_)

        if note:
            return GqlNote.from_db(note)

    async def resolve_pagination(self, info, page: int, per_page: int, patient_id: str):
        notes_queryset = DbNote.objects().filter(patientId=patient_id)

        notes_count = notes_queryset.count()
        notes = (notes_queryset
                 .skip(page * per_page)
                 .limit(per_page)
                 .order_by("-createdAt")
                 .all())

        pagination = NotePagination()
        pagination.page_info = PaginationInfo(page=page, per_page=per_page, total_items=notes_count)
        pagination.items = [GqlNote.from_db(note) for note in notes]

        return pagination
