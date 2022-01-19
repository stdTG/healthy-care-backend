from mongoengine import Document, EmbeddedDocument
from mongoengine.fields import DateTimeField, EmailField, EmbeddedDocumentField, StringField


class WorkspaceDb(EmbeddedDocument):
    host_alias = StringField(required=True)
    db_name = StringField()


class WorkspaceAwsCognito(EmbeddedDocument):
    aws_region = StringField()
    user_pool_id = StringField(required=True)
    dashboard_client_id = StringField(required=True)
    mobile_client_id = StringField(required=True)


class SystemUser(EmbeddedDocument):
    user_id = StringField()
    nickname = StringField()
    access_token = StringField()


class WorkspaceSendbird(EmbeddedDocument):
    app_id = StringField()
    app_name = StringField()
    master_api_token = StringField()
    master_api_token_created = DateTimeField()
    region = StringField()
    system_user = EmbeddedDocumentField(SystemUser, default=lambda: SystemUser())

    dashboard_token = StringField()
    dashboard_token_created = DateTimeField(required=False)
    dashboard_token_expiration = DateTimeField(required=False)


class WorkspaceS3Bucket(EmbeddedDocument):
    aws_region = StringField()
    name = StringField()


class WorkspaceStepFunctions(EmbeddedDocument):
    iam_role_arn = StringField()
    lambda_celery_client_arn = StringField()


class Workspace(Document):
    meta = {
        "db_alias": "master-db",
        "collection": "workspaces",
        "strict": False,
    }

    short_name = StringField(required=True, unique=True, max_length=64)
    human_friendly_name = StringField(required=True)  # It"s fine that this field name is long.
    # Workspaces collection isn"t going to be huge.

    tenant_db_1 = EmbeddedDocumentField(WorkspaceDb, required=True)
    tenant_db_2 = EmbeddedDocumentField(WorkspaceDb, required=True)

    admin_email = EmailField(required=True)
    admin_phone_number = StringField(required=True)
    aws_region = StringField(required=True)
    cognito = EmbeddedDocumentField(WorkspaceAwsCognito, default=lambda: WorkspaceAwsCognito())
    sendbird: WorkspaceSendbird = EmbeddedDocumentField(WorkspaceSendbird,
                                                        default=lambda: WorkspaceSendbird())
    s3 = EmbeddedDocumentField(WorkspaceS3Bucket,
                               default=lambda: WorkspaceS3Bucket())
    step_functions = EmbeddedDocumentField(WorkspaceStepFunctions,
                                           default=lambda: WorkspaceStepFunctions())

    @classmethod
    def get_db_name_1(cls, short_name: str):
        return short_name + "_1"

    @classmethod
    def get_db_name_2(cls, short_name: str):
        return short_name + "_2"


class WorkspaceSimple(Document):
    meta = {
        "db_alias": "master-db",
        "collection": "workspaces",
        "strict": False,
    }

    short_name = StringField(required=True, unique=True, max_length=64)
    human_friendly_name = StringField(required=True)
    admin_email = EmailField(required=True)
