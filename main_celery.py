import mongoengine
import celery
import celery.signals
from web.core.results import CamelModel

from core.config import get_app_config
from core.factory.celery import get_celery_app

from app.tenant_db_hosts.model_db import DbHost
from app.tenant_workspaces.model_db import Workspace, WorkspaceDb
from app.context import get_public_workspace_by_short_name


def register_tenant_dbs(workspace):

    def register_tenant_connection(workspace_db: WorkspaceDb, alias="default"):
        db: DbHost = DbHost.objects(alias=workspace_db.host_alias).first()

        mongoengine.disconnect(alias)
        mongoengine.register_connection(
            alias=alias,
            host=db.get_db_connection_string(workspace_db.db_name)
        )

    cfg = get_app_config()

    wks = get_public_workspace_by_short_name(workspace)
    register_tenant_connection(wks.tenant_db_1, "tenant-db-basic-data")
    register_tenant_connection(wks.tenant_db_2, "tenant-db-personal-data")


def register_master_db():

    cfg = get_app_config()
    
    mongoengine.register_connection(
        alias='master-db',
        host=cfg.MASTER_DB_CONNECTION
    )

@celery.signals.task_prerun.connect
def task_prerun(task_id, task, *args, **kwargs):
    kwargs = kwargs["kwargs"]
    workspace = kwargs["workspace"]
    print(f"task_prerun [workspace = {workspace}]")
    register_tenant_dbs(workspace)

register_master_db()

app = get_celery_app()
app.autodiscover_tasks(["app.care_plans.celery"], related_name="tasks")
app.autodiscover_tasks(["app.care_plans.celery"], related_name="tasks_widgets")
app.autodiscover_tasks(["app.feed.celery"], related_name="tasks")
