import pymongo

from app.tenant_db_hosts.model_db import DbHost
from app.tenant_workspaces.model_db import WorkspaceDb


def create_database(workspace_db: WorkspaceDb):
    db_host: DbHost = DbHost.objects(alias=workspace_db.host_alias).first()
    connection = db_host.get_db_connection_string(workspace_db.db_name)
    client = pymongo.MongoClient(connection)
    db = client[workspace_db.db_name]

    # this is necessary because Mongo doesn't actually
    # create a database until any collection is created
    db.create_collection('_stub')


def drop_database(workspace_db: WorkspaceDb):
    try:
        db_host: DbHost = DbHost.objects(alias=workspace_db.host_alias).first()
        connection = db_host.get_db_connection_string(workspace_db.db_name)
        client = pymongo.MongoClient(connection)
        client.drop_database(workspace_db.db_name)
    except Exception as error:
        print(str(error))
