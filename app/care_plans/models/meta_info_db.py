from mongoengine import Document, StringField


class Prefix(Document):
    meta = {
        "db_alias": "tenant-db-basic-data",
        "collection": "widgets_prefix",
        "strict": False
    }

    full_title = StringField(required=True)
    short_title = StringField(required=True)


class Category(Document):
    meta = {
        "db_alias": "tenant-db-basic-data",
        "collection": "widgets_category",
        "strict": False
    }

    title = StringField(required=True)


class WidgetDataType(Document):
    meta = {
        "db_alias": "tenant-db-basic-data",
        "collection": "widgets_user_data_type",
        "strict": False
    }
    """display_name - field displayed on dashboard,
     user_field - field where the user's answer is saved to the patient's card.
    """
    display_name = StringField(required=True)
    user_field = StringField(required=True)
