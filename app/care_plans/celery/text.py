import app.care_plans.models.widgets_db as widget_models
import app.feed.models.questions_web as message_models
import core.aws.sfn as sfn
import core.sendbird.messages as sbm
from app.care_plans.logic.question_handler import QuestionHandlerHelper
from app.context import get_public_workspace_by_short_name
from app.users.common.models.db import PatientUser
from core.config import get_app_config
from core.factory.celery import get_celery_app

capp = get_celery_app()
cfg = get_app_config()


class WidgetText_Helper(QuestionHandlerHelper):

    def __init__(self):
        super().__init__("MESSAGE")

    def create_message_prompt(self, widget: widget_models.Text, callback_token: str,
                              cp_as_id: str):
        body = message_models.MessageBody_Text_Prompt(text=widget.text,
                                                      version="1.0.0",
                                                      )
        msg = message_models.Message_Text_Prompt(type=message_models.MessageTypePrompt.text,
                                                 body=body,
                                                 care_plan_assignment_id=cp_as_id,
                                                 version="1.0.0"
                                                 )

        return msg

    def get_prompt_widget(self, widget_id) -> widget_models.Text:
        return widget_models.Text.objects(id=widget_id).first()


@capp.task(name="care_plans.question.text")
def run_care_plans_text_prompt(care_plan_assignment_id="", widget_id="", task_token="",
                               workspace=""):
    helper = WidgetText_Helper()
    wks = get_public_workspace_by_short_name(workspace)
    cp_assgn = helper.get_care_plan_assignment(care_plan_assignment_id)
    question = helper.get_prompt_widget(widget_id)

    patient = PatientUser.objects.with_id(cp_assgn.patient_id)
    message = helper.create_message_prompt(question, task_token, care_plan_assignment_id)
    json_message = message.json()

    sbm_client = sbm.SendbirdMessages(wks.sendbird.app_id,
                                      wks.sendbird.master_api_token,
                                      patient.sendbird.feed_channel_url)
    sbm_client.send(json_message, cfg.SENDBIRD_SYSTEM_ACCOUNT)

    sfn.AwsStepFunctions("eu-west-3").send_task_success(task_token)
