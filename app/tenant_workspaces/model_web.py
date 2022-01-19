from typing import Optional

from pydantic import Field

from web.core import ObjectIdStr
from web.core.results import CamelModel


class WorkspaceDb(CamelModel):
    host_alias: str
    db_name: Optional[str]


class WorkspaceAwsCognito(CamelModel):
    user_pool_id: Optional[str]
    dashboard_client_id: Optional[str]
    mobile_client_id: Optional[str]


class AdminUser(CamelModel):
    email: str
    phoneNumber: str
    password: Optional[str]


class DbHosts(CamelModel):
    hostAlias1: str
    hostAlias2: str


class Workspace(CamelModel):
    shortName: str
    fullName: str
    awsRegion: str

    dbHosts: DbHosts
    admin: AdminUser


class WorkspaceSimple(CamelModel):
    id: Optional[ObjectIdStr] = None

    short_name: str
    full_name: str
    admin_email: str


class WorkspacePublicOut(CamelModel):
    short_name: str = Field(alias="workspace")
    human_friendly_name: str = Field(alias="fullName")
    aws_region: str
    user_pool_id: str
    dashboard_client_id: str = Field(alias="clientId")
    dashboard_client_id: str
    mobile_client_id: str
