from typing import List

from fastapi import Depends

from app.users.common.models.db import PatientUser
from web.cloudauth.auth_claims import AuthClaims
from web.cloudauth.auth_current_user import AuthCurrentUser
from .router import router_mobile
from ..models.db import Metric
from ..models.web import MetricData, Metrics, Metric as WebMetric

get_current_user = AuthCurrentUser()


@router_mobile.get("/", response_model=Metrics)
async def get_patient_metrics(current_user: AuthClaims = Depends(get_current_user)):
    patient = PatientUser.objects(cognito_sub=current_user.sub).first()
    metrics_qs = Metric.objects(patient_id=patient.id)

    metrics: List[Metric] = (metrics_qs
               .order_by("-date")
               .all())

    if not metrics:
        return []

    processed_metric = []
    curr_metric = metrics[0].widget_data_type_id
    metrics_web = []
    for metric in metrics:
        if metric.widget_data_type_id in processed_metric:
            continue

        values = []
        for mtr in metrics:
            if mtr.widget_data_type_id == curr_metric:
                values.append(MetricData(date=mtr.created, value=mtr.value))

        metric_web = WebMetric(name=metric.widget_data_type_name, values=values)
        metrics_web.append(metric_web)
        processed_metric.append(metric.widget_data_type_id)

    return Metrics(metrics=metrics_web)
