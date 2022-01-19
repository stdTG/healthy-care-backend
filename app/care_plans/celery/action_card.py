import json

import app.care_plans.models.widgets_db as widget_models
import app.feed.models.questions_web as message_models
import core.aws.sfn as sfn
import core.sendbird.messages as sbm
from app.care_plans.logic.question_handler import QuestionHandlerHelper
from app.care_plans.models.meta_info_db import Category
from app.context import get_public_workspace_by_short_name
from app.users.common.models.db import PatientUser
from core.config import get_app_config
from core.factory.celery import get_celery_app

capp = get_celery_app()
cfg = get_app_config()


class WidgetAction_Card_Helper(QuestionHandlerHelper):

    def __init__(self):
        super().__init__("ACTION_CARD")

    def create_message_prompt(self, widget: widget_models.ActionCard, callback_token: str,
                              cp_as_id: str):
        # TODO define version of widget
        category = Category.objects.with_id(widget.categoryId).title

        body = message_models.MessageBody_Action_Card_Prompt(category=category,
                                                             description=widget.description,
                                                             tips=widget.tips,
                                                             url=widget.url,
                                                             )
        msg = message_models.Message_Question_Text_Prompt(type=widget.celeryTaskPrompt,
                                                          body=body,
                                                          care_plan_assignment_id=cp_as_id,
                                                          version="1.0.0"
                                                          )

        return msg

    def get_prompt_widget(self, widget_id) -> widget_models.ActionCard:
        return widget_models.ActionCard.objects(id=widget_id).first()


@capp.task(name="care_plans.question.action_card_prompt")
def run_care_plans_action_card_prompt(care_plan_assignment_id="", widget_id="", taskToken="",
                                      workspace=""):
    helper = WidgetAction_Card_Helper()
    wks = get_public_workspace_by_short_name(workspace)
    cp_assgn = helper.get_care_plan_assignment(care_plan_assignment_id)
    question = helper.get_prompt_widget(widget_id)

    patient = PatientUser.objects.with_id(cp_assgn.patient_id)
    message = helper.create_message_prompt(question, taskToken, care_plan_assignment_id)
    json_message = json.dumps(message, default=lambda x: x.__dict__)

    sbm_client = sbm.SendbirdMessages(wks.sendbird.app_id,
                                      wks.sendbird.master_api_token,
                                      patient.sendbird.feed_channel_url)
    sbm_client.send(json_message, cfg.SENDBIRD_SYSTEM_ACCOUNT)

    sfn.AwsStepFunctions("eu-west-3").send_task_success(taskToken)
