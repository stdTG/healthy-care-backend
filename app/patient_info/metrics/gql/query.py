import graphene

from ..models.db import Metric
from ..models.gql import Metric as GqlMetric


class MetricQueries(graphene.ObjectType):
    pagination = graphene.Field(
        type=graphene.List(GqlMetric),
        patient_id=graphene.ID(required=True, name="patient")
    )

    async def resolve_pagination(self, _, patient_id: str):
        metrics_qs = Metric.objects(patient_id=patient_id)

        metrics = (metrics_qs
                   .order_by("-date")
                   .all())

        items = [GqlMetric.from_db(metric) for metric in metrics]

        return items
