import uuid

from mongoengine import EmbeddedDocument
from mongoengine.fields import DateField, StringField, UUIDField


class Allergy(EmbeddedDocument):
    uuid = UUIDField(default=lambda: str(uuid.uuid4()))
    name = StringField(required=True)
    date = DateField()
