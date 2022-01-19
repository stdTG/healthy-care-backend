import mongoengine
import mongoengine.fields as fields

from app.tenant_db_hosts.model_db import DbHost
from app.tenant_workspaces.model_db import WorkspaceDb
from core.config import Config


def register_master_connection(cfg: Config):
    mongoengine.register_connection(
        alias='master-db',
        host=cfg.MASTER_DB_CONNECTION
    )


async def register_tenant_connection(cfg: Config, workspace_db: WorkspaceDb, alias="default"):
    db: DbHost = DbHost.objects(alias=workspace_db.host_alias).first()

    mongoengine.disconnect(alias)
    mongoengine.register_connection(
        alias=alias,
        host=db.get_db_connection_string(workspace_db.db_name)
    )


def map(document, data_dict):
    def field_value(field, value):

        if field.__class__ in (fields.ListField, fields.SortedListField):
            return [
                field_value(field.field, item)
                for item in value
            ]
        if field.__class__ in (
                fields.EmbeddedDocumentField,
                fields.GenericEmbeddedDocumentField,
                fields.ReferenceField,
                fields.GenericReferenceField
        ):
            return field.document_type(**value)
        else:
            return value

    [setattr(
        document, key,
        field_value(document._fields[key], value)
    ) for key, value in data_dict.items()]

    return document
