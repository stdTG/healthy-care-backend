from mongoengine import Document, StringField


class DbHost(Document):
    meta = {
        "db_alias": "master-db",
        "collection": "db_hosts",
        "strict": False
    }

    alias = StringField(required=True, unique=True)
    name = StringField(required=True)
    description = StringField()

    db_host = StringField()
    db_user = StringField()
    db_password = StringField()

    # Example: "mongodb+srv://{user}:{password}@{host}/{dbname}"
    connection_string_format = StringField(required=True,
                                           default="mongodb://{user}:{password}@{host}/{dbname}")

    def get_db_connection_string(self, dbname):
        if self.db_user and self.db_password:
            return self.connection_string_format.format(
                user=self.db_user,
                password=self.db_password,
                host=self.db_host,
                dbname=dbname,
            )
        else:
            return "mongodb://{host}/{dbname}".format(
                host=self.db_host,
                dbname=dbname,
            )
