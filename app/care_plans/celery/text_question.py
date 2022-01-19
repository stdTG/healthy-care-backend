from datetime import datetime

import app.care_plans.models.care_plan_db as cp_models
import app.care_plans.models.widgets_db as widget_models
import app.feed.models.questions_web as message_models
import core.aws.sfn as sfn
from app.care_plans.logic.question_handler import QuestionHandler, QuestionHandlerHelper
from app.patient_info.notes.models.db import Note
from core.factory.celery import get_celery_app

capp = get_celery_app()


class WidgetQuestion_Text_Helper(QuestionHandlerHelper):

    def __init__(self):
        super().__init__("TEXT")

    def create_message_prompt(self, question: widget_models.Question_Text, callback_token: str,
                              cp_as_id: str):
        # TODO define version of widget
        body = message_models.MessageBody_Question_Text_Prompt(prompt=question.question_text,
                                                               version="1.0.0")
        msg = message_models.Message_Question_Text_Prompt(type=question.question_text,
                                                          body=body,
                                                          care_plan_assignment_id=cp_as_id,
                                                          callback_token=callback_token,
                                                          version="1.0.0"
                                                          )

        return msg

    def get_prompt_widget(self, widget_id) -> cp_models.Question:
        return widget_models.Question_Text.objects(id=widget_id).first()

    def save_response(self, cp: cp_models.CarePlanAssignment,
                      widget_data: cp_models.WidgetPatientData,
                      widget: cp_models.Question):
        note = Note()
        note.title = widget.question_text
        note.content = widget_data.data
        note.patientId = cp.patient_id
        note.createdAt = datetime.now()

        note.save()


@capp.task(name="care_plans.question.text_question_prompt")
def run_care_plans_question_text_prompt(care_plan_assignment_id="", widget_id="", task_token="",
                                        workspace=""):
    # Show patient inputbox: Please enter your name
    QuestionHandler(WidgetQuestion_Text_Helper()).prompt(
        care_plan_assignment_id=care_plan_assignment_id,
        widget_id=widget_id,
        task_token=task_token,
        workspace=workspace, )


@capp.task(name="care_plans.question.text_question_response")
def run_care_plans_question_text_response(care_plan_assignment_id="", message="", task_token="",
                                          workspace=""):
    QuestionHandler(WidgetQuestion_Text_Helper()).response(care_plan_assignment_id, message,
                                                           task_token)
    sfn.AwsStepFunctions("eu-west-3").send_task_success(task_token)
