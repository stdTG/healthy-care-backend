from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from mongoengine import Document
from mongoengine.fields import DateTimeField, ObjectIdField, StringField

if TYPE_CHECKING:
    from ..gql.inputs import NoteCreateInput


class Note(Document):
    meta = {
        "db_alias": "tenant-db-basic-data",
        "collection": "notes",
        "strict": False
    }

    title = StringField(required=True)
    content = StringField()
    createdById = ObjectIdField(required=True)
    patientId = ObjectIdField(required=True)
    createdAt = DateTimeField(required=True)
    updatedAt = DateTimeField()

    @classmethod
    def from_gql(cls, input_: NoteCreateInput, created_by_id: str):
        return cls(
            title=input_.title,
            content=input_.content,
            createdById=created_by_id,
            patientId=input_.patient,
            createdAt=datetime.now(),
            updatedAt=None
        )
