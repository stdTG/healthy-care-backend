import app.booking.web as booking
import app.feed.web as feed
import app.metadata as metadata
import app.org_units.web as org_units
import app.settings.mobile as mobile_settings
import app.super_admin.migrations as super_admin_migrations
import app.patient_info.metrics.web as metrics
import app.sendbird as super_admin_sendbird
import app.super_admin.workflows as super_admin_workflows
import app.tenant_db_hosts.web as super_admin_db_hosts
import app.tenant_workspaces.web as super_admin_workspaces
import app.users.auth as mobile_auth
import app.users.mobile.patient as mobile_patient
from .graphql import init_graphql


def init_routes():
    print("[APP] Init Router")

    metadata.init_router()

    feed.init_router()
    org_units.init_router()
    mobile_settings.init_router()
    booking.init_router()
    metrics.init_router()

    mobile_auth.init_router()
    mobile_patient.init_router()

    super_admin_migrations.init_router()
    super_admin_sendbird.init_router()
    super_admin_workflows.init_router()
    super_admin_db_hosts.init_router()
    super_admin_workspaces.init_router()

    init_graphql()
