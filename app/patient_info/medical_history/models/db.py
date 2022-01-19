from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..gql.inputs import MedicalHistoryInput

from mongoengine import Document, ObjectIdField
from mongoengine.fields import (DateField, StringField)


class MedicalHistory(Document):
    meta = {
        "db_alias": "tenant-db-personal-data",
        "collection": "medical_history",
        "strict": False
    }

    patientId = ObjectIdField()
    name = StringField()
    date = DateField()
    comment = StringField()

    @classmethod
    def from_gql(cls, gql: MedicalHistoryInput) -> MedicalHistory:
        db = cls()

        db.patientId = gql.patient_id
        db.name = gql.name
        db.date = gql.date
        db.comment = gql.comment

        return db
