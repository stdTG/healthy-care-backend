from typing import List, Union

from bson import ObjectId

from ..model_db import OrgUnit as DbOrgUnit


async def get_orgs(ids: Union[List[str], List[ObjectId]]) -> List[DbOrgUnit]:
    """It also return master organization."""
    ids = list(map(str, ids))
    return sorted(DbOrgUnit.objects(pk__in=ids).all(), key=lambda a: ids.index(str(a.id)))


async def get_care_teams(ids: List[str]):
    res = list(DbOrgUnit.objects.aggregate([
        {
            "$match": {
                "parentId": {
                    "$in": ids
                }
            }
        },
        {
            "$group": {
                "_id": "$parentId",
                "careTeams": {
                    "$push": "$$ROOT"
                }
            }
        }
    ]))
    # elements come from the database in a random order, but the dataloader wants them in the order
    # in which the IDs come. it is fast decision.

    sort_res = []
    for id_ in ids:
        obj = find_by_id(id_, res)
        sort_res.append(obj)
    return sort_res


def find_by_id(id_, lst):
    for el in lst:
        if el.get("_id") == id_:
            return el
