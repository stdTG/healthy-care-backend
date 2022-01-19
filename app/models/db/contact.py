from mongoengine import EmbeddedDocument
from mongoengine.fields import StringField


class Contact(EmbeddedDocument):
    type = StringField(required=True)
    value = StringField(required=True)
