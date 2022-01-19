import app.care_plans.models.widgets_db as widget_models
import app.feed.models.questions_web as message_models
import core.aws.sfn as sfn
from app.care_plans.logic.question_handler import QuestionHandler, QuestionHandlerHelper
from core.factory.celery import get_celery_app

capp = get_celery_app()


class WidgetQuestion_NumberScale_Helper(QuestionHandlerHelper):

    def __init__(self):
        super().__init__("NUMBER_SCALE")

    def get_prompt_widget(self, widget_id):
        return widget_models.Question_NumberScale.objects(id=widget_id).first()

    def create_message_prompt(self, question: widget_models.Question_NumberScale,
                              callback_token: str, cp_as_id: str):
        body = message_models.MessageBody_Question_NumberScale_Prompt(
            prompt=question.question_text,
            start_scale=question.start_scale,
            end_scale=question.end_scale,
            left_label=question.left_label,
            right_label=question.right_label,
            center_label=question.center_label,
            scores=[{"start": score.start_value,
                     "end": score.end_value,
                     "score": score.result_score}
                    for score in question.scores],

        )
        msg = message_models.Message_Question_NumberScale_Prompt(
            type=message_models.MessageTypePrompt.number_scale,
            body=body,
            care_plan_assignment_id=cp_as_id,
            callback_token=callback_token,
            version="1.0.0"
        )

        return msg


@capp.task(name="care_plans.question.number_scale_prompt")
def run_care_plans_question_number_scale_prompt(care_plan_assignment_id="", widget_id="",
                                                task_token="",
                                                workspace=""):
    QuestionHandler(WidgetQuestion_NumberScale_Helper()).prompt(
        care_plan_assignment_id=care_plan_assignment_id,
        widget_id=widget_id,
        task_token=task_token,
        workspace=workspace, )


@capp.task(name="care_plans.question.number_scale_response")
def run_care_plans_question_number_scale_response(care_plan_assignment_id="", message="",
                                                  task_token="",
                                                  workspace=""):
    QuestionHandler(WidgetQuestion_NumberScale_Helper()).response(care_plan_assignment_id, message,
                                                                  task_token)
    sfn.AwsStepFunctions("eu-west-3").send_task_success(task_token)
