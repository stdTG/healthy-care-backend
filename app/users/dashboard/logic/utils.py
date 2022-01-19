import re
from collections import OrderedDict
from typing import List, Union

from bson import ObjectId

from ...common.models.db import DashboardUser as DbUser, PatientUser as DbPatient


async def get_users(ids: Union[List[str], List[ObjectId]]) -> List[DbUser]:
    ids = list(map(str, ids))
    return sorted(DbUser.objects(pk__in=ids).all(), key=lambda a: ids.index(str(a.id)))


async def get_patients(ids: Union[List[str], List[ObjectId]]) -> List[DbPatient]:
    ids = list(map(str, ids))
    return sorted(DbPatient.objects(pk__in=ids).all(), key=lambda a: ids.index(str(a.id)))


async def get_users_by_org_unit(ids: List[str]):
    users: List[DbUser] = DbUser.objects(orgUnitId__in=ids, deleted=False).all()
    users_by_org = OrderedDict()
    for id_ in ids:
        users_by_org[id_] = []

    # rewrite
    for id_ in ids:
        for user in users:
            if user.orgUnitId == id_:
                users_by_org[id_].append(user)

    return users_by_org.values()


def create_regexp(str_: str):
    str_ = str_.lower()
    return re.compile(f".*{str_}.*", re.IGNORECASE)
