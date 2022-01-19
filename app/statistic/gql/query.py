from datetime import date

import graphene

from app.users.common.models.db import PatientUser as Patient
from .inputs import FilterStatistic
from .payloads import StatisticPayload
from ...org_units.model_db import OrgUnit


class StatisticsQueries(graphene.ObjectType):
    by_gender = graphene.Field(
        type=StatisticPayload,
        filter_=FilterStatistic(name="filter"),
    )
    by_age = graphene.Field(
        type=StatisticPayload,
        filter_=FilterStatistic(name="filter"),
    )
    by_location = graphene.Field(
        type=StatisticPayload,
        filter_=FilterStatistic(name="filter"),
    )

    async def resolve_by_gender(self, _, **kwargs):
        filter_: FilterStatistic = kwargs.get("filter", None)
        queryset = Patient.objects()

        if filter_ and filter_.deleted:
            queryset = queryset.filter(deleted__ne=filter_.deleted)

        if filter_ and filter_.care_team_id:
            queryset = queryset.filter(orgUnitId=filter_.care_team_id)

        if filter_ and filter_.sub_org_id:
            care_teams = OrgUnit.objects(parentId=filter_.sub_org_id).all()
            org_unit_ids = [cm.id for cm in care_teams]
            org_unit_ids.append(filter_.sub_org_id)

            queryset = queryset.filter(orgUnitId__in=org_unit_ids)

        res = list(queryset.aggregate({
            "$group": {"_id": "$sex", "count": {"$sum": 1}}
        }))

        output = [{"key": item["_id"], "value": item["count"]} for item in res]
        return StatisticPayload(items=output)

    async def resolve_by_age(self, _, **kwargs):
        filter_: FilterStatistic = kwargs.get("filter", None)
        queryset = Patient.objects()

        if filter_ and filter_.deleted:
            queryset = queryset.filter(deleted__ne=filter_.deleted)

        if filter_ and filter_.care_team_id:
            queryset = queryset.filter(orgUnitId=filter_.care_team_id)

        if filter_ and filter_.sub_org_id:
            care_teams = OrgUnit.objects(parentId=filter_.sub_org_id).all()
            org_unit_ids = [cm.id for cm in care_teams]
            org_unit_ids.append(filter_.sub_org_id)

            queryset = queryset.filter(orgUnitId__in=org_unit_ids)

        res = list(queryset.aggregate([
            {
                "$group": {
                    "_id": {"year": {"$year": "$birthDate"}},
                    "count": {"$sum": 1}}
            },
            {
                "$sort": {"_id.year": -1}
            }
        ]))
        curr_year = date.today().year

        output = []
        for item in res:
            if item["_id"]["year"] is None:
                output.append({"key": -1, "value": item["count"]})
                continue

            output.append({"key": curr_year - item["_id"]["year"], "value": item["count"]})
        return StatisticPayload(items=sorted(output, key=lambda lst: lst["key"]))

    async def resolve_by_location(self, _, **kwargs):
        filter_: FilterStatistic = kwargs.get("filter", None)
        queryset = Patient.objects()

        if filter_ and filter_.deleted:
            queryset = queryset.filter(deleted__ne=filter_.deleted)

        if filter_ and filter_.care_team_id:
            queryset = queryset.filter(orgUnitId=filter_.care_team_id)

        if filter_ and filter_.sub_org_id:
            care_teams = OrgUnit.objects(parentId=filter_.sub_org_id).all()
            org_unit_ids = [cm.id for cm in care_teams]
            org_unit_ids.append(filter_.sub_org_id)

            queryset = queryset.filter(orgUnitId__in=org_unit_ids)

        res = list(queryset.aggregate([
            {
                "$unwind": "$address"
            },
            {
                "$group": {
                    "_id": {"$toLower": "$address.city"},
                    "count": {"$sum": 1}}
            },
            {
                "$sort": {"count": -1}
            }
        ]))

        output = []
        for item in res:
            if not item["_id"]:
                item["_id"] = "empty"

            output.append(
                {"key": item["_id"], "value": item["count"]}
            )

        return StatisticPayload(items=output)
