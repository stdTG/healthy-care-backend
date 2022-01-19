import json

from fastapi import Depends, Request, status

from app.context import get_current_workspace
from app.feed.models.questions_web import *
from core.errors import HTTPNotAllowedError, HTTPNotFoundError
from core.factory.celery import get_celery_app
from core.sendbird.messages import SendbirdMessages
from web.cloudauth.auth_claims import AuthClaims
from web.cloudauth.auth_current_user import AuthCurrentUser
from .router import router_questions
from .web_tests_questions import CELERY_PATH
from ..models.questions_web import MessageTypeResponse
from ...care_plans.models.care_plan_db import CarePlanAssignment
from ...users.common.models.db import PatientUser

route_settings = {
    "status_code": status.HTTP_204_NO_CONTENT,
    "responses": {
        204: {"description": "Message successfully sent"},
        500: {"description": "Server error"}
    }
}

get_current_user = AuthCurrentUser()
celery_app = get_celery_app()


@router_questions.post("/prompt", **route_settings)
async def feed_message_prompt(request: Request,
                              input_: Message_Question,
                              current_user: AuthClaims = Depends(
                                  get_current_user)):
    workspace = await get_current_workspace(request)
    task_name = await get_task_name(input_.type)
    cp_assign: CarePlanAssignment = \
        CarePlanAssignment.objects.with_id(input_.care_plan_assignment_id)

    if not task_name:
        raise HTTPNotFoundError(message="message type not found")

    patient: PatientUser = PatientUser.objects.filter(id=cp_assign.patient_id).first()
    if not patient:
        raise HTTPNotFoundError(message="patient not found")

    # if patient.cognito_sub != current_user.sub:
    #     raise HTTPNotAllowedError()

    await send_sendbird_message(input_, workspace.sendbird.app_id,
                                workspace.sendbird.master_api_token,
                                patient.sendbird.feed_channel_url)

    await create_job(input_, workspace.short_name, task_name)


async def send_sendbird_message(message: Message_Question, app_id: str, token: str, feed_url: str):
    json_message = message.json(by_alias=True)

    sbm_client = SendbirdMessages(app_id, token, feed_url)
    await sbm_client.async_send(json_message)


async def create_job(input_: Message_Question, workspace_name: str, task_name: str):
    celery_app.send_task(task_name,
                         kwargs={
                             "care_plan_assignment_id": input_.care_plan_assignment_id,
                             "task_token": input_.callback_token,
                             "workspace": workspace_name,
                             "message": json.dumps(input_, default=lambda x: x.__dict__),
                         })


async def get_task_name(message_type: str):
    tasks = {
        MessageTypeResponse.text: CELERY_PATH + "text_response",
        MessageTypeResponse.yes_no: CELERY_PATH + "yes_no_response",
        MessageTypeResponse.number_simple: CELERY_PATH + "number_simple_response",
        MessageTypeResponse.time: CELERY_PATH + "time_response",
        MessageTypeResponse.rating: CELERY_PATH + "rating_response",
        MessageTypeResponse.phone: CELERY_PATH + "phone_response",
        MessageTypeResponse.multiple_choice: CELERY_PATH + "multiple_choice_response",
        MessageTypeResponse.labels: CELERY_PATH + "labels_response",
        MessageTypeResponse.picture_choice: CELERY_PATH + "picture_choice_response",
        MessageTypeResponse.date: CELERY_PATH + "date_response",
        MessageTypeResponse.address: CELERY_PATH + "address_response",
        MessageTypeResponse.number_scale: CELERY_PATH + "number_scale_response",
    }

    return tasks.get(MessageTypeResponse(message_type), None)
