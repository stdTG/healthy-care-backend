from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..gql.inputs import MedicalConditionInput

from mongoengine import Document, EmbeddedDocument
from mongoengine.fields import (DateField, StringField, ObjectIdField, UUIDField
                                )


class MedicalCondition(Document):
    meta = {
        "db_alias": "master-db",
        "collection": "medical_condition",
        "strict": False
    }

    name = StringField(required=True)


class MedicalConditionPatient(EmbeddedDocument):
    name = StringField()
    uuid = UUIDField(default=lambda: str(uuid.uuid4()))
    index = ObjectIdField()  # relative from medical condition document
    start = DateField()
    end = DateField()

    @classmethod
    def from_gql(cls, input_: MedicalConditionInput, name: str) -> MedicalConditionPatient:
        db = cls()

        db.name = name
        db.index = input_.index
        db.start = input_.start
        db.end = input_.end

        return db
