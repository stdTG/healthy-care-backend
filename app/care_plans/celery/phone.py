import app.care_plans.models.care_plan_db as cp_models
import app.care_plans.models.widgets_db as widget_models
import app.feed.models.questions_web as message_models
import core.aws.sfn as sfn
from app.care_plans.logic.question_handler import QuestionHandler, QuestionHandlerHelper
from app.users.common.models.db import PatientUser as Patient
from core.factory.celery import get_celery_app

capp = get_celery_app()


class WidgetQuestion_Phone_Helper(QuestionHandlerHelper):

    def __init__(self):
        super().__init__("PHONE")

    def get_prompt_widget(self, widget_id):
        return widget_models.Question_Phone.objects(id=widget_id).first()

    def create_message_prompt(self, question: widget_models.Question_Phone, callback_token: str,
                              cp_as_id: str):
        body = message_models.MessageBody_Question_Phone_Prompt(prompt=question.question_text,
                                                                code=question.countryCode,
                                                                )
        msg = message_models.Message_Question_Phone_Prompt(type=question.celeryTaskPrompt,
                                                           body=body,
                                                           care_plan_assignment_id=cp_as_id,
                                                           callback_token=callback_token,
                                                           version="1.0.0"
                                                           )

        return msg

    def save_response(self, cp: cp_models.CarePlanAssignment,
                      widget_data: cp_models.WidgetPatientData,
                      widget: cp_models.Question):
        patient = Patient.objects.with_id(cp.patient_id)
        patient.phone = widget_data.data
        patient.save()


@capp.task(name="care_plans.question.phone_prompt")
def run_care_plans_question_phone_prompt(care_plan_assignment_id="", widget_id="", task_token="",
                                         workspace=""):
    QuestionHandler(WidgetQuestion_Phone_Helper()).prompt(
        care_plan_assignment_id=care_plan_assignment_id,
        widget_id=widget_id,
        task_token=task_token,
        workspace=workspace, )


@capp.task(name="care_plans.question.phone_response")
def run_care_plans_question_phone_response(care_plan_assignment_id="", message="", task_token="",
                                           workspace=""):
    QuestionHandler(WidgetQuestion_Phone_Helper()).response(care_plan_assignment_id, message,
                                                            task_token)
    sfn.AwsStepFunctions("eu-west-3").send_task_success(task_token)
