from typing import List

import app.care_plans.models.care_plan_db as cp_models
import core.aws.sfn as sfn
from app.care_plans.logic.calculator import calculate_formula_handler
from app.care_plans.logic.question_handler import QuestionHandlerHelper
from app.care_plans.logic.rules import process_rule
from app.care_plans.models.widgets_db import Calculator
from core.factory.celery import get_celery_app

capp = get_celery_app()


class WidgetCalculator_Helper(QuestionHandlerHelper):

    def __init__(self):
        super().__init__("CALCULATOR")

    def create_message_prompt(self, widget: Calculator, callback_token: str,
                              cp_as_id: str):
        pass

    def get_prompt_widget(self, widget_id) -> Calculator:
        return Calculator.objects(id=widget_id).first()


@capp.task(name="care_plans.question.calculator_prompt")
def run_care_plans_action_card_prompt(care_plan_assignment_id="", widget_id="", taskToken="",
                                      workspace=""):
    helper = WidgetCalculator_Helper()
    cp_assgn = helper.get_care_plan_assignment(care_plan_assignment_id)
    calculator_widget = helper.get_prompt_widget(widget_id)

    variables = {}  # variables for insert into formula
    widgets_data = (
        cp_models.WidgetPatientData.objects(aws_execution_id=cp_assgn.aws_execution_id)
            .all()
    )

    widgets = (
        cp_models.DbWidget.objects(carePlanId=cp_assgn.care_plan_id)
            .all()
    )

    for widget in widgets:
        widget_data = get_widget_data(widgets_data, widget.id)
        widget_score = process_rule(widget.scoreRules, widget_data.data)
        variables[widget.scoreVarName] = widget_score

    score = calculate_formula_handler(calculator_widget.formula, variables=variables)
    sfn.AwsStepFunctions("eu-west-3").send_task_success(taskToken, score=score)


def get_widget_data(widgets_data: List[cp_models.WidgetPatientData], widget_id: str):
    for widget_data in widgets_data:
        if widget_data.widget_id == widget_id:
            return widget_data
