import uuid

from mongoengine import EmbeddedDocument
from mongoengine.fields import StringField, UUIDField


class Lifestyle(EmbeddedDocument):
    uuid = UUIDField(default=lambda: str(uuid.uuid4()))
    activity = StringField(required=True)
    description = StringField()
