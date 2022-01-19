from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.org_units.gql.inputs import SubOrgUpdateInput

from app.users.common.models.db import DashboardUser as User

from app.org_units.model_db import OrgUnit
from app.models.db import Address


def update_sub_org_handler(sub_org: OrgUnit, record: SubOrgUpdateInput):
    sub_org.name = record.name
    sub_org.email = record.email
    sub_org.phone = record.phone
    sub_org.site = record.site
    sub_org.address = Address.from_gql(
        record.full_address) if record.full_address else Address()
    sub_org.supervisors = record.supervisors
    sub_org.save()

    if isinstance(record.user_ids, list):
        User.objects(orgUnitId=sub_org.id).update(set__orgUnitId=None)
        User.objects(pk__in=record.user_ids).update(set__orgUnitId=sub_org.id)

    if isinstance(record.care_team_ids, list):
        new_care_team_ids = set(record.care_team_ids)
        __update_care_teams(sub_org, new_care_team_ids)


def __update_care_teams(sub_org: OrgUnit, new_care_team_ids):
    old_care_teams = OrgUnit.objects.filter(parentId=sub_org.id).all()
    old_care_team_ids = {ct.id for ct in old_care_teams}

    deleted_ids = old_care_team_ids - new_care_team_ids
    new_ids = new_care_team_ids - old_care_team_ids

    OrgUnit.objects(pk__in=deleted_ids).update(set__parentId=None)
    OrgUnit.objects(pk__in=new_ids).update(set__parentId=sub_org.id)
