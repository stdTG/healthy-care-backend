import app.care_plans.models.widgets_db as widget_models
import app.feed.models.questions_web as message_models
import core.aws.sfn as sfn
from app.care_plans.logic.question_handler import QuestionHandler, QuestionHandlerHelper
from app.care_plans.models.meta_info_db import Prefix
from core.factory.celery import get_celery_app

capp = get_celery_app()


class WidgetQuestion_NumberSimple_Helper(QuestionHandlerHelper):

    def __init__(self):
        super().__init__("NUMBER_SIMPLE")

    def get_prompt_widget(self, widget_id) -> widget_models.Question_NumberSimple:
        return widget_models.Question_NumberSimple.objects(id=widget_id).first()

    def create_message_prompt(self, question: widget_models.Question_NumberSimple,
                              callback_token: str, cp_as_id: str):
        # prefix = Prefix.objects.with_id(question.prefix_id)
        body = message_models.MessageBody_Question_NumberSimple_Prompt(
            version="1.0.0",
            prompt=question.question_text,
            min=question.min,
            max=question.max,
            # prefix=f"{prefix.full_title - prefix.short_title}"
            prefix="",
        )
        msg = message_models.Message_Question_NumberSimple_Prompt(
            body=body,
            care_plan_assignment_id=cp_as_id,
            callback_token=callback_token,
            version="1.0.0"
        )

        return msg


@capp.task(name="care_plans.question.number_simple_prompt")
def run_care_plans_question_number_simple_prompt(care_plan_assignment_id="", widget_id="",
                                                 task_token="",
                                                 workspace=""):
    QuestionHandler(WidgetQuestion_NumberSimple_Helper()).prompt(
        care_plan_assignment_id=care_plan_assignment_id,
        widget_id=widget_id,
        task_token=task_token,
        workspace=workspace, )


@capp.task(name="care_plans.question.number_simple_response")
def run_care_plans_question_number_simple_response(care_plan_assignment_id="", message="",
                                                   task_token="", workspace=""):
    QuestionHandler(WidgetQuestion_NumberSimple_Helper()).response(care_plan_assignment_id, message,
                                                                   task_token)
    sfn.AwsStepFunctions("eu-west-3").send_task_success(task_token)
