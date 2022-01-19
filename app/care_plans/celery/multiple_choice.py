import json

import app.care_plans.models.widgets_db as widget_models
import app.feed.models.questions_web as message_models
import core.aws.sfn as sfn
from app.care_plans.logic.question_handler import QuestionHandler, QuestionHandlerHelper
from core.factory.celery import get_celery_app

capp = get_celery_app()


class WidgetQuestion_MultipleChoice_Helper(QuestionHandlerHelper):

    def __init__(self):
        super().__init__("MULTIPLE_CHOICE")

    def get_prompt_widget(self, widget_id):
        return widget_models.Question_MultipleChoice.objects(id=widget_id).first()

    def create_message_prompt(self, question: widget_models.Question_MultipleChoice,
                              callback_token: str, cp_as_id: str):
        body = message_models.MessageBody_Question_MultipleChoice_Prompt(
            version="1.0.0",
            prompt=question.question_text,
            multiselect=question.is_multiselect,
            answers=[{"text": ans.text, "number": ans.number} for ans in question.answers],
        )
        msg = message_models.Message_Question_MultipleChoice_Prompt(
            type=message_models.MessageTypePrompt.multiple_choice,
            body=body,
            care_plan_assignment_id=cp_as_id,
            callback_token=callback_token,
            version="1.0.0"
        )

        return msg


@capp.task(name="care_plans.question.multiple_choice_prompt")
def run_care_plans_question_multiple_choice_prompt(care_plan_assignment_id="", widget_id="",
                                                   task_token="", workspace=""):
    QuestionHandler(WidgetQuestion_MultipleChoice_Helper()).prompt(
        care_plan_assignment_id=care_plan_assignment_id,
        widget_id=widget_id,
        task_token=task_token,
        workspace=workspace, )


@capp.task(name="care_plans.question.multiple_choice_response")
def run_care_plans_question_multiple_choice_response(care_plan_assignment_id="", message="",
                                                     task_token="", workspace=""):
    QuestionHandler(WidgetQuestion_MultipleChoice_Helper()).response(care_plan_assignment_id,
                                                                     message,
                                                                     task_token)
    msg = json.loads(message)
    select = msg.get("body").get("user_response")
    sfn.AwsStepFunctions("eu-west-3").send_choice_success(task_token, select)
