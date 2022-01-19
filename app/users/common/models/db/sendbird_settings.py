from mongoengine import EmbeddedDocument
from mongoengine.fields import ListField, StringField


class SendbirdSettings(EmbeddedDocument):
    feed_channel_url = StringField()
    access_token = StringField()
    session_tokens = ListField()
