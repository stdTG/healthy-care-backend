from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .db import MedicalHistory as DbMed

import graphene


class MedicalHistory(graphene.ObjectType):
    id_ = graphene.ID()
    name = graphene.String()
    date = graphene.Date()
    comment = graphene.String()

    @classmethod
    def from_db(cls, db: DbMed) -> MedicalHistory:
        gql = cls()
        gql.id_ = db.id
        gql.name = db.name
        gql.date = db.date
        gql.comment = db.comment

        return gql
