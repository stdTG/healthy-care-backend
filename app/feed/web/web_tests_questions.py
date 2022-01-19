import json
from typing import Any

from fastapi import Depends, Request, status

from app.context import get_current_workspace
from app.feed.models.questions_web import *
from core.factory.celery import get_celery_app
from web.cloudauth.auth_claims import AuthClaims
from web.cloudauth.auth_current_user import AuthCurrentUser
from .router import router_tests_questions

CELERY_PATH = "care_plans.question."
route_settings = {
    "status_code": status.HTTP_204_NO_CONTENT,
    "responses": {
        204: {"description": "Message successfully sent"},
        500: {"description": "Server error"}
    }
}

get_current_user = AuthCurrentUser()
celery_app = get_celery_app()


@router_tests_questions.post("/text-prompt", **route_settings)
async def feed_test_message_question_text_prompt(request: Request,
                                                 input_: Message_Question_Text_Prompt,
                                                 current_user: AuthClaims = Depends(
                                                     get_current_user)):
    workspace = await get_current_workspace(request)
    celery_app.send_task(CELERY_PATH + "text_prompt",
                         kwargs={
                             "care_plan_assignment_id": input_.care_plan_assignment_id,
                             "task_token": input_.callback_token,
                             "workspace": workspace.short_name,
                             "message": json.dumps(input_, default=lambda x: x.__dict__),
                         })


@router_tests_questions.post("/text-response", **route_settings)
async def feed_test_message_question_text_response(request: Request,
                                                   input_: Any,
                                                   current_user: AuthClaims = Depends(
                                                       get_current_user),
                                                   ):
    workspace = await get_current_workspace(request)
    celery_app.send_task(CELERY_PATH + "text_response",
                         kwargs={
                             "care_plan_assignment_id": input_.care_plan_assignment_id,
                             "task_token": input_.callback_token,
                             "workspace": workspace.short_name,
                             "message": json.dumps(input_, default=lambda x: x.__dict__),
                         })


@router_tests_questions.post("/number-simple-prompt", **route_settings)
async def feed_test_message_question_number_simple_prompt(
        request: Request,
        input_: Message_Question_NumberSimple_Prompt,
        current_user: AuthClaims = Depends(get_current_user)):
    workspace = await get_current_workspace(request)
    celery_app.send_task(CELERY_PATH + "number_simple_prompt",
                         kwargs={
                             "care_plan_assignment_id": input_.care_plan_assignment_id,
                             "task_token": input_.callback_token,
                             "workspace": workspace.short_name,
                             "message": json.dumps(input_, default=lambda x: x.__dict__),
                         })


@router_tests_questions.post("/number-simple-response", **route_settings)
async def feed_test_message_question_number_simple_response(request: Request,
                                                            input_: Message_Question_NumberSimple_Response,
                                                            current_user: AuthClaims = Depends(
                                                                get_current_user)):
    workspace = await get_current_workspace(request)
    celery_app.send_task(CELERY_PATH + "number_simple_response",
                         kwargs={
                             "care_plan_assignment_id": input_.care_plan_assignment_id,
                             "task_token": input_.callback_token,
                             "workspace": workspace.short_name,
                             "message": json.dumps(input_, default=lambda x: x.__dict__),
                         })


@router_tests_questions.post("/number-scale-prompt", **route_settings)
async def feed_test_message_question_number_scale_prompt(
        request: Request,
        input_: Message_Question_NumberScale_Prompt,
        current_user: AuthClaims = Depends(
            get_current_user)):
    workspace = await get_current_workspace(request)
    celery_app.send_task(CELERY_PATH + "number_scale_prompt",
                         kwargs={
                             "care_plan_assignment_id": input_.care_plan_assignment_id,
                             "task_token": input_.callback_token,
                             "workspace": workspace.short_name,
                             "message": json.dumps(input_, default=lambda x: x.__dict__),
                         })


@router_tests_questions.post("/number-scale-response", **route_settings)
async def feed_test_message_question_number_scale_response(
        request: Request,
        input_: Message_Question_NumberScale_Response,
        current_user: AuthClaims = Depends(
            get_current_user)):
    workspace = await get_current_workspace(request)
    celery_app.send_task(CELERY_PATH + "number_scale_response",
                         kwargs={
                             "care_plan_assignment_id": input_.care_plan_assignment_id,
                             "task_token": input_.callback_token,
                             "workspace": workspace.short_name,
                             "message": json.dumps(input_, default=lambda x: x.__dict__),
                         })


@router_tests_questions.post("/address-prompt", **route_settings)
async def feed_test_message_question_address_prompt(
        request: Request, input_: Message_Question_Address_Prompt,
        current_user: AuthClaims = Depends(
            get_current_user)):
    workspace = await get_current_workspace(request)
    celery_app.send_task(CELERY_PATH + "address_prompt",
                         kwargs={
                             "care_plan_assignment_id": input_.care_plan_assignment_id,
                             "task_token": input_.callback_token,
                             "workspace": workspace.short_name,
                             "message": json.dumps(input_, default=lambda x: x.__dict__),
                         })


@router_tests_questions.post("/address-response", **route_settings)
async def feed_test_message_question_address_response(request: Request,
                                                      input_: Message_Question_Address_Response,
                                                      current_user: AuthClaims = Depends(
                                                          get_current_user)):
    workspace = await get_current_workspace(request)
    celery_app.send_task(CELERY_PATH + "address_response",
                         kwargs={
                             "care_plan_assignment_id": input_.care_plan_assignment_id,
                             "task_token": input_.callback_token,
                             "workspace": workspace.short_name,
                             "message": json.dumps(input_, default=lambda x: x.__dict__),
                         })


@router_tests_questions.post("/date-prompt", **route_settings)
async def feed_test_message_question_date_prompt(request: Request,
                                                 input_: Message_Question_Date_Prompt,
                                                 current_user: AuthClaims = Depends(
                                                     get_current_user)):
    workspace = await get_current_workspace(request)
    celery_app.send_task(CELERY_PATH + "date_prompt",
                         kwargs={
                             "care_plan_assignment_id": input_.care_plan_assignment_id,
                             "task_token": input_.callback_token,
                             "workspace": workspace.short_name,
                             "message": json.dumps(input_, default=lambda x: x.__dict__),
                         })


@router_tests_questions.post("/date-response", **route_settings)
async def feed_test_message_question_date_response(request: Request,
                                                   input_: Message_Question_Date_Response,
                                                   current_user: AuthClaims = Depends(
                                                       get_current_user)):
    workspace = await get_current_workspace(request)
    celery_app.send_task(CELERY_PATH + "date_response",
                         kwargs={
                             "care_plan_assignment_id": input_.care_plan_assignment_id,
                             "task_token": input_.callback_token,
                             "workspace": workspace.short_name,
                             "message": json.dumps(input_, default=lambda x: x.__dict__),
                         })


@router_tests_questions.post("/file-upload-prompt", **route_settings)
async def feed_test_message_question_file_upload_prompt(request: Request,
                                                        input_: Message_Question_FileUpload_Prompt,
                                                        current_user: AuthClaims = Depends(
                                                            get_current_user)):
    workspace = await get_current_workspace(request)
    celery_app.send_task(CELERY_PATH + "file_upload_prompt",
                         kwargs={
                             "care_plan_assignment_id": input_.care_plan_assignment_id,
                             "task_token": input_.callback_token,
                             "workspace": workspace.short_name,
                             "message": json.dumps(input_, default=lambda x: x.__dict__),
                         })


@router_tests_questions.post("/file-upload-response", **route_settings)
async def feed_test_message_question_file_upload_response(request: Request,
                                                          input_: Message_Question_FileUpload_Response,
                                                          current_user: AuthClaims = Depends(
                                                              get_current_user)):
    workspace = await get_current_workspace(request)
    celery_app.send_task(CELERY_PATH + "file_upload_response",
                         kwargs={
                             "care_plan_assignment_id": input_.care_plan_assignment_id,
                             "task_token": input_.callback_token,
                             "workspace": workspace.short_name,
                             "message": json.dumps(input_, default=lambda x: x.__dict__),
                         })


@router_tests_questions.post("/labels-prompt", **route_settings)
async def feed_test_message_question_labels_prompt(request: Request,
                                                   input_: Message_Question_Labels_Prompt,
                                                   current_user: AuthClaims = Depends(
                                                       get_current_user)):
    workspace = await get_current_workspace(request)
    celery_app.send_task(CELERY_PATH + "labels_prompt",
                         kwargs={
                             "care_plan_assignment_id": input_.care_plan_assignment_id,
                             "task_token": input_.callback_token,
                             "workspace": workspace.short_name,
                             "message": json.dumps(input_, default=lambda x: x.__dict__),
                         })


@router_tests_questions.post("/labels-response", **route_settings)
async def feed_test_message_question_labels_response(request: Request,
                                                     input_: Message_Question_Labels_Response,
                                                     current_user: AuthClaims = Depends(
                                                         get_current_user)):
    workspace = await get_current_workspace(request)
    celery_app.send_task(CELERY_PATH + "labels_response",
                         kwargs={
                             "care_plan_assignment_id": input_.care_plan_assignment_id,
                             "task_token": input_.callback_token,
                             "workspace": workspace.short_name,
                             "message": json.dumps(input_, default=lambda x: x.__dict__),
                         })


@router_tests_questions.post("/multiple-choice-prompt", **route_settings)
async def feed_test_message_question_multiple_choice_prompt(
        request: Request,
        input_: Message_Question_MultipleChoice_Prompt,
        current_user: AuthClaims = Depends(get_current_user)):
    workspace = await get_current_workspace(request)
    celery_app.send_task(CELERY_PATH + "multiple_choice_prompt",
                         kwargs={
                             "care_plan_assignment_id": input_.care_plan_assignment_id,
                             "task_token": input_.callback_token,
                             "workspace": workspace.short_name,
                             "message": json.dumps(input_, default=lambda x: x.__dict__),
                         })


@router_tests_questions.post("/multiple-choice-response", **route_settings)
async def feed_test_message_question_multiple_choice_response(
        request: Request,
        input_: Message_Question_MultipleChoice_Response,
        current_user: AuthClaims = Depends(
            get_current_user)):
    workspace = await get_current_workspace(request)
    celery_app.send_task(CELERY_PATH + "multiple_choice_response",
                         kwargs={
                             "care_plan_assignment_id": input_.care_plan_assignment_id,
                             "task_token": input_.callback_token,
                             "workspace": workspace.short_name,
                             "message": json.dumps(input_, default=lambda x: x.__dict__),
                         })


@router_tests_questions.post("/phone-prompt", **route_settings)
async def feed_test_message_question_phone_prompt(request: Request,
                                                  input_: Message_Question_Phone_Prompt,
                                                  current_user: AuthClaims = Depends(
                                                      get_current_user)):
    workspace = await get_current_workspace(request)
    celery_app.send_task(CELERY_PATH + "phone_prompt",
                         kwargs={
                             "care_plan_assignment_id": input_.care_plan_assignment_id,
                             "task_token": input_.callback_token,
                             "workspace": workspace.short_name,
                             "message": json.dumps(input_, default=lambda x: x.__dict__),
                         })


@router_tests_questions.post("/phone-response", **route_settings)
async def feed_test_message_question_phone_response(request: Request,
                                                    input_: Message_Question_Phone_Response,
                                                    current_user: AuthClaims = Depends(
                                                        get_current_user)):
    workspace = await get_current_workspace(request)
    celery_app.send_task(CELERY_PATH + "phone_response",
                         kwargs={
                             "care_plan_assignment_id": input_.care_plan_assignment_id,
                             "task_token": input_.callback_token,
                             "workspace": workspace.short_name,
                             "message": json.dumps(input_, default=lambda x: x.__dict__),
                         })


@router_tests_questions.post("/picture-choice-prompt", **route_settings)
async def feed_test_message_question_picture_choice_prompt(
        request: Request,
        input_: Message_Question_PictureChoice_Prompt,
        current_user: AuthClaims = Depends(get_current_user)):
    workspace = await get_current_workspace(request)
    celery_app.send_task(CELERY_PATH + "picture_choice_prompt",
                         kwargs={
                             "care_plan_assignment_id": input_.care_plan_assignment_id,
                             "task_token": input_.callback_token,
                             "workspace": workspace.short_name,
                             "message": json.dumps(input_, default=lambda x: x.__dict__),
                         })


@router_tests_questions.post("/picture-choice-response", **route_settings)
async def feed_test_message_question_picture_choice_response(
        request: Request,
        input_: Message_Question_PictureChoice_Response,
        current_user: AuthClaims = Depends(
            get_current_user)
):
    workspace = await get_current_workspace(request)
    celery_app.send_task(CELERY_PATH + "picture_choice_response",
                         kwargs={
                             "care_plan_assignment_id": input_.care_plan_assignment_id,
                             "task_token": input_.callback_token,
                             "workspace": workspace.short_name,
                             "message": json.dumps(input_, default=lambda x: x.__dict__),
                         })


@router_tests_questions.post("/rating-prompt", **route_settings)
async def feed_test_message_question_rating_prompt(request: Request,
                                                   input_: Message_Question_Rating_Prompt,
                                                   current_user: AuthClaims = Depends(
                                                       get_current_user)):
    workspace = await get_current_workspace(request)
    celery_app.send_task(CELERY_PATH + "rating-prompt",
                         kwargs={
                             "care_plan_assignment_id": input_.care_plan_assignment_id,
                             "task_token": input_.callback_token,
                             "workspace": workspace.short_name,
                             "message": json.dumps(input_, default=lambda x: x.__dict__),
                         })


@router_tests_questions.post("/rating-response", **route_settings)
async def feed_test_message_question_rating_response(request: Request,
                                                     input_: Message_Question_Rating_Response,
                                                     current_user: AuthClaims = Depends(
                                                         get_current_user)):
    workspace = await get_current_workspace(request)
    celery_app.send_task(CELERY_PATH + "rating_response",
                         kwargs={
                             "care_plan_assignment_id": input_.care_plan_assignment_id,
                             "task_token": input_.callback_token,
                             "workspace": workspace.short_name,
                             "message": json.dumps(input_, default=lambda x: x.__dict__),
                         })


@router_tests_questions.post("/time-prompt", **route_settings)
async def feed_test_message_question_time_prompt(request: Request,
                                                 input_: Message_Question_Time_Prompt,
                                                 current_user: AuthClaims = Depends(
                                                     get_current_user)):
    workspace = await get_current_workspace(request)
    celery_app.send_task(CELERY_PATH + "time-prompt",
                         kwargs={
                             "care_plan_assignment_id": input_.care_plan_assignment_id,
                             "task_token": input_.callback_token,
                             "workspace": workspace.short_name,
                             "message": json.dumps(input_, default=lambda x: x.__dict__),
                         })


@router_tests_questions.post("/time-response", **route_settings)
async def feed_test_message_question_time_response(request: Request,
                                                   input_: Message_Question_Time_Response,
                                                   current_user: AuthClaims = Depends(
                                                       get_current_user)):
    workspace = await get_current_workspace(request)
    celery_app.send_task(CELERY_PATH + "time_response",
                         kwargs={
                             "care_plan_assignment_id": input_.care_plan_assignment_id,
                             "task_token": input_.callback_token,
                             "workspace": workspace.short_name,
                             "message": json.dumps(input_, default=lambda x: x.__dict__),
                         })


@router_tests_questions.post("/yes-no-prompt", **route_settings)
async def feed_test_message_question_yes_no_prompt(request: Request,
                                                   input_: Message_Question_YesNo_Prompt,
                                                   current_user: AuthClaims = Depends(
                                                       get_current_user)):
    workspace = await get_current_workspace(request)
    celery_app.send_task(CELERY_PATH + "yes_no_prompt",
                         kwargs={
                             "care_plan_assignment_id": input_.care_plan_assignment_id,
                             "task_token": input_.callback_token,
                             "workspace": workspace.short_name,
                             "message": json.dumps(input_, default=lambda x: x.__dict__),
                         })


@router_tests_questions.post("/action-widget", **route_settings)
async def feed_test_message_question_action_widget_prompt(request: Request,
                                                   input_: Message_Action_Card_Prompt,
                                                   current_user: AuthClaims = Depends(
                                                       get_current_user)):
    workspace = await get_current_workspace(request)
    celery_app.send_task(CELERY_PATH + "action_card_prompt",
                         kwargs={
                             "care_plan_assignment_id": input_.care_plan_assignment_id,
                             "task_token": input_.callback_token,
                             "workspace": workspace.short_name,
                             "message": json.dumps(input_, default=lambda x: x.__dict__),
                         })


@router_tests_questions.post("/yes-no-response", **route_settings)
async def feed_test_message_question_yes_no_response(request: Request,
                                                     input_: Message_Question_YesNo_Response,
                                                     current_user: AuthClaims = Depends(
                                                         get_current_user)):
    workspace = await get_current_workspace(request)
    celery_app.send_task(CELERY_PATH + "yes_no_response",
                         kwargs={
                             "care_plan_assignment_id": input_.care_plan_assignment_id,
                             "task_token": input_.callback_token,
                             "workspace": workspace.short_name,
                             "message": json.dumps(input_, default=lambda x: x.__dict__),
                         })
