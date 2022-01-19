import app.care_plans.models.widgets_db as widget_models
import app.feed.models.questions_web as message_models
import core.aws.sfn as sfn
from app.care_plans.logic.question_handler import QuestionHandler, QuestionHandlerHelper
from core.factory.celery import get_celery_app

capp = get_celery_app()


class WidgetQuestion_Date_Helper(QuestionHandlerHelper):

    def __init__(self):
        super().__init__("DATE")

    def get_prompt_widget(self, widget_id):
        return widget_models.Question_Date.objects(id=widget_id).first()

    def create_message_prompt(self, question: widget_models.Question_Date, callback_token: str,
                              cp_as_id: str):
        body = message_models.MessageBody_Question_Date_Prompt(prompt=question.question_text,
                                                               format=question.format, )
        msg = message_models.Message_Question_Date_Prompt(type=question.celeryTaskPrompt,
                                                          body=body,
                                                          care_plan_assignment_id=cp_as_id,
                                                          callback_token=callback_token,
                                                          version="1.0.0"
                                                          )

        return msg


@capp.task(name="care_plans.question.date_prompt")
def run_care_plans_question_date_prompt(care_plan_assignment_id="", widget_id="", task_token="",
                                        workspace=""):
    QuestionHandler(WidgetQuestion_Date_Helper()).prompt(
        care_plan_assignment_id=care_plan_assignment_id,
        widget_id=widget_id,
        task_token=task_token,
        workspace=workspace, )


@capp.task(name="care_plans.question.date_response")
def run_care_plans_question_date_response(care_plan_assignment_id="", message="", taskToken="",
                                          workspace=""):
    QuestionHandler(WidgetQuestion_Date_Helper()).response(care_plan_assignment_id, message,
                                                           taskToken)
    sfn.AwsStepFunctions("eu-west-3").send_task_success(taskToken)
