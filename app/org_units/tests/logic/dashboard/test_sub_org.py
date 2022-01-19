from typing import List

import pytest

from app.org_units.logic.dashboard.sub_org import __update_care_teams
from app.org_units.model_db import OrgUnit
from app.user_roles import Roles
from app.users.common.models.db import DashboardUser as User, DashboardUser
from app.org_units.tests.conftest import db_sub_org
from app.users.tests.conftest import db_users
from tests.database.conftest import db_connections


@pytest.mark.parametrize("db_users", [(15, Roles.DOCTOR)], indirect=["db_users", ])
def test_update_care_team_for_db_org(db_connections, db_sub_org, db_users: List[User]):
    """Test delete 2 care teams"""
    assert len(db_users) == 15
    assert len(User.objects.all()) == 15

    users_care_team1 = db_users[:4]
    users_care_team2 = db_users[4:7]
    users_care_team3 = db_users[7:8]
    users_sub_org = db_users[8:11]
    users_free = db_users[11:]

    care_team1 = OrgUnit(name="care_team1",
                         parentId=db_sub_org.id,
                         isCareTeam=True, ).save()
    care_team2 = OrgUnit(name="care_team2",
                         parentId=db_sub_org.id,
                         isCareTeam=True, ).save()
    care_team3 = OrgUnit(name="care_team3",
                         parentId=db_sub_org.id,
                         isCareTeam=True, ).save()

    for user in users_care_team1:
        user.orgUnitId = care_team1.id
        user.save()

    for user in users_care_team2:
        user.orgUnitId = care_team2.id
        user.save()

    for user in users_care_team3:
        user.orgUnitId = care_team3.id
        user.save()

    for user in users_free:
        user.save()

    for user in users_sub_org:
        user.orgUnitId = db_sub_org.id
        user.save()

    care_teams = OrgUnit.objects.filter(parentId=db_sub_org.id, isCareTeam=True).all()
    users = DashboardUser.objects.filter(
        orgUnitId__in=[cm.id for cm in care_teams] + [db_sub_org.id]
    ).all()

    assert len(users) == len(users_sub_org) + len(users_care_team1)\
           + len(users_care_team2) + len(users_care_team3)

    input_ = {care_team2.id}
    __update_care_teams(db_sub_org, input_)

    care_teams = OrgUnit.objects.filter(parentId=db_sub_org.id, isCareTeam=True).all()
    assert len(care_teams) == 1
    assert care_teams[0].id == care_team2.id

    users = DashboardUser.objects.filter(
        orgUnitId__in=[cm.id for cm in care_teams] + [db_sub_org.id]
    ).all()

    assert len(users) == len(users_sub_org) + len(users_care_team2)


@pytest.mark.parametrize("db_users", [(15, Roles.DOCTOR)], indirect=["db_users", ])
def test_update_care_team_for_db_org2(db_connections, db_sub_org, db_users: List[User]):
    """Test delete all care teams"""
    assert len(db_users) == 15
    assert len(User.objects.all()) == 15

    users_care_team1 = db_users[:4]
    users_care_team2 = db_users[4:7]
    users_care_team3 = db_users[7:8]
    users_sub_org = db_users[8:11]
    users_free = db_users[11:]

    care_team1 = OrgUnit(name="care_team1",
                         parentId=db_sub_org.id,
                         isCareTeam=True, ).save()
    care_team2 = OrgUnit(name="care_team2",
                         parentId=db_sub_org.id,
                         isCareTeam=True, ).save()
    care_team3 = OrgUnit(name="care_team3",
                         parentId=db_sub_org.id,
                         isCareTeam=True, ).save()

    for user in users_care_team1:
        user.orgUnitId = care_team1.id
        user.save()

    for user in users_care_team2:
        user.orgUnitId = care_team2.id
        user.save()

    for user in users_care_team3:
        user.orgUnitId = care_team3.id
        user.save()

    for user in users_free:
        user.save()

    for user in users_sub_org:
        user.orgUnitId = db_sub_org.id
        user.save()

    input_ = set()
    __update_care_teams(db_sub_org, input_)

    care_teams = OrgUnit.objects.filter(parentId=db_sub_org.id, isCareTeam=True).all()
    assert len(care_teams) == 0

    users = DashboardUser.objects.filter(
        orgUnitId__in=[cm.id for cm in care_teams] + [db_sub_org.id]
    ).all()

    assert len(users) == len(users_sub_org)


@pytest.mark.parametrize("db_users", [(15, Roles.DOCTOR)], indirect=["db_users", ])
def test_update_care_team_for_db_org3(db_connections, db_sub_org, db_users: List[User]):
    """Test adding 2 care teams"""
    assert len(db_users) == 15
    assert len(User.objects.all()) == 15

    users_care_team1 = db_users[:4]
    users_care_team2 = db_users[4:7]
    users_care_team3 = db_users[7:8]
    users_sub_org = db_users[8:11]
    users_free = db_users[11:]

    care_team1 = OrgUnit(name="care_team1",
                         parentId=db_sub_org.id,
                         isCareTeam=True, ).save()
    care_team2 = OrgUnit(name="care_team2",
                         parentId=None,
                         isCareTeam=True, ).save()
    care_team3 = OrgUnit(name="care_team3",
                         parentId=None,
                         isCareTeam=True, ).save()

    for user in users_care_team1:
        user.orgUnitId = care_team1.id
        user.save()

    for user in users_care_team2:
        user.orgUnitId = care_team2.id
        user.save()

    for user in users_care_team3:
        user.orgUnitId = care_team3.id
        user.save()

    for user in users_free:
        user.save()

    for user in users_sub_org:
        user.orgUnitId = db_sub_org.id
        user.save()

    input_ = {care_team1.id, care_team2.id, care_team3.id}
    __update_care_teams(db_sub_org, input_)

    care_teams = OrgUnit.objects.filter(parentId=db_sub_org.id, isCareTeam=True).all()
    assert len(care_teams) == 3

    users = DashboardUser.objects.filter(
        orgUnitId__in=[cm.id for cm in care_teams] + [db_sub_org.id]
    ).all()

    assert len(users) == len(users_sub_org) + len(users_care_team1) + len(users_care_team2) +\
           len(users_care_team3)


