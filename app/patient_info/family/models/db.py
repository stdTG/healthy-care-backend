from mongoengine import EmbeddedDocument
from mongoengine.fields import ListField


class Family(EmbeddedDocument):
    mother = ListField(default=lambda: list())
    father = ListField(default=lambda: list())
    grandparents = ListField(default=lambda: list())
    grandmother = ListField()
    grandfather = ListField()
