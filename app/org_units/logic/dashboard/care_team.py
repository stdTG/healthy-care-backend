from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.org_units.gql.inputs import CareTeamUpdateInput

from app.users.common.models.db import DashboardUser as User

from app.org_units.model_db import OrgUnit


def update_care_team_handler(care_team: OrgUnit, record: CareTeamUpdateInput):
    care_team.name = record.name
    care_team.supervisors = record.supervisors
    care_team.parentId = record.sub_org_id
    care_team.save()

    if isinstance(record.users, list):
        User.objects(orgUnitId=care_team.id).update(set__orgUnitId=None)
        User.objects(pk__in=record.users).update(set__orgUnitId=care_team.id)
