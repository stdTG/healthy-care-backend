import json

import app.care_plans.models.care_plan_db as cp_models
import app.care_plans.models.widgets_db as widget_models
import core.sendbird.messages as sbm
from app.context import get_public_workspace_by_short_name
from app.users.common.models.db import PatientUser as Patient
from core.config import get_app_config

cfg = get_app_config()


class QuestionHandlerHelper:

    def __init__(self, name):
        self.name = name

    def get_care_plan_assignment(self, carePlanAssgnId) -> cp_models.CarePlanAssignment:
        return cp_models.CarePlanAssignment.objects(id=carePlanAssgnId).first()

    def get_care_plan(self, carePlanId) -> cp_models.DbCarePlan:
        return cp_models.DbCarePlan.objects(id=carePlanId).first()

    def get_prompt_widget(self, widget_id) -> widget_models.Question_Text:
        pass

    def create_message_prompt(self, question: cp_models.Question, callback_token: str,
                              cp_as_id: str):
        pass

    def save_response(self, cp: cp_models.CarePlanAssignment,
                      widget_data: cp_models.WidgetPatientData,
                      widget: cp_models.Question):
        """If need to save answer to the another place."""
        pass


class QuestionHandler:

    def __init__(self, helper: QuestionHandlerHelper):
        self.helper = helper

    def prompt(self, care_plan_assignment_id="", widget_id="", task_token="", workspace=""):
        msg = f"[{self.helper.name}] | {care_plan_assignment_id} | {widget_id} | {task_token[-10:]}"
        print(msg)

        cp_assgn = self.helper.get_care_plan_assignment(care_plan_assignment_id)
        question = self.helper.get_prompt_widget(widget_id)
        wks = get_public_workspace_by_short_name(workspace)

        patient = Patient.objects.with_id(cp_assgn.patient_id)

        message = self.helper.create_message_prompt(question, task_token, care_plan_assignment_id)
        json_message = message.json(by_alias=True)

        widget_data = cp_models.WidgetPatientData()
        widget_data.widget_id = widget_id
        widget_data.task_token = task_token
        widget_data.assignment_id = cp_assgn.id
        widget_data.save()

        sbm_client = sbm.SendbirdMessages(wks.sendbird.app_id,
                                          wks.sendbird.master_api_token,
                                          patient.sendbird.feed_channel_url)
        sbm_client.send(json_message, cfg.SENDBIRD_SYSTEM_ACCOUNT)

    def response(self, care_plan_assignment_id="", message="", task_token=""):
        msg = f"[{self.helper.name}] | {care_plan_assignment_id} | {message}"
        print(msg)

        cp_assign = self.helper.get_care_plan_assignment(care_plan_assignment_id)
        widget_data = cp_models.WidgetPatientData.objects(task_token=task_token).first()

        widget = self.helper.get_prompt_widget(widget_data.widget_id)

        if not widget_data:
            print(
                f"widget data did not find for cp_assigment_id:"
                f" {cp_assign}, task_token: {task_token}")
            return

        message = json.loads(message)
        widget_data.data = message.get("body").get("user_response")
        widget_data.status = str(cp_models.WidgetStatus.OK)
        widget_data.save()

        self.helper.save_response(cp_assign, widget_data, widget)
