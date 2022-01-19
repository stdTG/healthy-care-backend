import json

from fastapi import Form, Request

from core.factory import celery
from web.cloudauth.auth_current_user import AuthCurrentUser
from .router import router_superadmin

get_current_user = AuthCurrentUser()


@router_superadmin.post("/workflows/start-aws-state-machine")
async def start_aws_state_machine(request: Request, stateMachineArn: str = Form(...)):
    # wks: Workspace = await get_current_workspace(request)
    capp = celery.get_celery_app()
    input_ = {
        "CarePlanId": "TEST_CarePlan",
        "PatientId": "TEST_Patient",
    }
    print(json.dumps(input_))
    capp.send_task("care_plans.start", [stateMachineArn, json.dumps(input_)])
    return "OK"
