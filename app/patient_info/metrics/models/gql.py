from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .db import Metric as DbMetric

import graphene


class Metric(graphene.ObjectType):
    created = graphene.DateTime()
    value = graphene.Int()
    widget_data_type_id = graphene.ID()
    widget_data_type_name = graphene.String()

    @classmethod
    def from_db(cls, db: DbMetric) -> Metric:
        gql = cls()
        gql.created = db.created
        gql.value = db.value
        gql.widget_data_type_id = db.widget_data_type_id
        gql.widget_data_type_name = db.widget_data_type_name

        return gql
