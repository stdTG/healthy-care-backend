import app.care_plans.celery.start
import app.care_plans.celery.stop
from app.care_plans.models.care_plan_db import CarePlanAssignment, DbCarePlan
from app.context import get_public_workspace_by_short_name
from core.factory.celery import get_celery_app

capp = get_celery_app()


@capp.task(name="care_plans.start")
def start(*args, **kwargs):
    cp_as_id = kwargs.get("care_plan_assignment_id")
    workspace_name = kwargs.get("workspace")

    wks = get_public_workspace_by_short_name(workspace_name)
    cp_as: CarePlanAssignment = CarePlanAssignment.objects.with_id(cp_as_id)
    cp: DbCarePlan = DbCarePlan.objects.with_id(cp_as.care_plan_id)

    res = app.care_plans.celery.start.run(
        input_={
            "workspace": wks.short_name,
            "carePlanAssignmentId": cp_as_id,
        },
        state_machine_arn=cp.aws_state_machine_arn,
    )
    cp_as.aws_execution_id = res["executionArn"]
    cp_as.execution_start_date_time = res["startDate"]
    cp_as.save()


@capp.task(name="care_plans.stop")
def stop(*args, **kwargs):
    app.care_plans.celery.stop.run(*args, **kwargs)
