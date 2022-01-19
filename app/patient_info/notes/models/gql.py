from __future__ import annotations

from typing import TYPE_CHECKING

from app.context import get_fields, get_loader
from app.users.common.models.gql import DashboardUser, PatientUser

if TYPE_CHECKING:
    from .db import Note as DbNote

import graphene


class Note(graphene.ObjectType):
    id = graphene.ID()
    title = graphene.String()
    content = graphene.String()
    created_by = graphene.Field(lambda: DashboardUser)
    patient = graphene.Field(lambda: PatientUser)
    created_at = graphene.DateTime()
    updated_at = graphene.DateTime()

    @staticmethod
    async def resolve_created_by(root, info):
        fields = get_fields(info)

        if root.created_by and not (len(fields) == 1 and "id_" in fields):
            loader = await get_loader(info, "user_by_id")
            db_user = await loader.load(root.created_by)
            return DashboardUser.from_db(db_user)
        elif root.created_by:
            return DashboardUser(id_=root.created_by)
        else:
            return None

    @staticmethod
    async def resolve_patient(root, info):
        fields = get_fields(info)

        if root.patient and not (len(fields) == 1 and "id_" in fields):
            loader = await get_loader(info, "patient_by_id")
            db_user = await loader.load(root.patient)
            return PatientUser.from_db(db_user)
        else:
            return PatientUser(id_=root.patient)

    @classmethod
    def from_db(cls, note: DbNote) -> Note:
        return cls(
            id=note.id,
            title=note.title,
            content=note.content,
            created_by=note.createdById,
            patient=note.patientId,
            created_at=note.createdAt,
            updated_at=note.updatedAt
        )
