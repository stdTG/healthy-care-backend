import app.care_plans.models.widgets_db as widget_models
import app.feed.models.questions_web as message_models
import core.aws.sfn as sfn
from app.care_plans.logic.question_handler import QuestionHandler, QuestionHandlerHelper
from core.factory.celery import get_celery_app

capp = get_celery_app()


class WidgetQuestion_YesNo_Helper(QuestionHandlerHelper):

    def __init__(self):
        super().__init__("YES_NO")

    def create_message_prompt(self, question: widget_models.Question_Text, callback_token: str,
                              cp_as_id: str):
        # TODO define version of widget
        body = message_models.MessageBody_Question_YesNo_Prompt(prompt=question.question_text,
                                                                version="1.0.0")
        msg = message_models.Message_Question_YesNo_Prompt(type=question.celeryTaskPrompt,
                                                           body=body,
                                                           care_plan_assignment_id=cp_as_id,
                                                           callback_token=callback_token,
                                                           version="1.0.0"
                                                           )

        return msg


@capp.task(name="care_plans.question.yes_no_prompt")
def run_care_plans_question_yes_no_prompt(care_plan_assignment_id="", widget_id="", task_token="",
                                          workspace=""):
    QuestionHandler(WidgetQuestion_YesNo_Helper()).prompt(
        care_plan_assignment_id=care_plan_assignment_id,
        widget_id=widget_id,
        task_token=task_token,
        workspace=workspace, )


@capp.task(name="care_plans.question.yes_no_response")
def run_care_plans_question_yes_no_response(care_plan_assignment_id="", message="", task_token="",
                                            workspace=""):
    QuestionHandler(WidgetQuestion_YesNo_Helper()).response(care_plan_assignment_id, message,
                                                            task_token)
    sfn.AwsStepFunctions("eu-west-3").send_task_success(task_token)
