from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .db import MedicalCondition as DbMed
    from .db import MedicalConditionPatient as DbMedPatient

import graphene


class MedicalCondition(graphene.ObjectType):
    id_ = graphene.ID()
    name = graphene.String()

    @classmethod
    def from_db(cls, db: DbMed) -> MedicalCondition:
        gql = cls()
        gql.id_ = db.id
        gql.name = db.name

        return gql


class MedicalConditionPatient(graphene.ObjectType):
    uuid = graphene.UUID()
    name = graphene.String()
    index = graphene.ID()
    start = graphene.Date(name="startDate")
    end = graphene.Date(name="endDate")

    @classmethod
    def from_db(cls, db: DbMedPatient) -> MedicalConditionPatient:
        gql = cls()
        gql.uuid = db.uuid
        gql.name = db.name
        gql.start = db.start
        gql.end = db.end
        gql.index = db.index

        return gql
