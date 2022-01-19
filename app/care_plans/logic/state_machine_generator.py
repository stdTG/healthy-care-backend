from typing import Dict

from app.care_plans.models.care_plan_db import DbCarePlan, DbWidget, Question
from app.care_plans.models.widgets_db import QUESTION_CELERY_TASKS, Question_MultipleChoice
from core.aws.sfn import Choice, Pass, StateMachine, Task


class AwsStateMachineGenerator:
    START_STEP_NAME = "Startup"
    FINISH_STEP_NAME = "Finish"

    TASK_RESOURCE__LAMBDA_WAIT_FOR_TOKEN = "arn:aws:states:::lambda:invoke.waitForTaskToken"

    def __init__(self, care_plan: DbCarePlan,
                 widgets: Dict[str, DbWidget],
                 lambda_celery_client_arn: str = "", ):
        self.carePlan = care_plan
        self.lambda_celery_client_arn = lambda_celery_client_arn
        self.widgets = widgets

        if not (self.carePlan and widgets and len(widgets) > 0):
            raise Exception("No widgets defined in CarePlan")

        self.sm = StateMachine(StartAt=self.START_STEP_NAME, TimeoutSeconds=300)

    def care_plan_to_json(self) -> str:

        self.__startup_step()
        self.__widget_steps()
        self.__finish_step()

        return self.sm.json(exclude_none=True, indent=4, sort_keys=False)

    def __startup_step(self):
        first_widget: DbWidget = [wd for wd in self.widgets.values() if wd.is_start_widget][0]
        self.sm.States[self.START_STEP_NAME] = Pass(
            Next=first_widget.name
        )

    def __finish_step(self):
        last_widget: DbWidget = [wd for wd in self.widgets.values() if not wd.next_widget][0]
        self.sm.States[self.FINISH_STEP_NAME] = Pass(
            End=True
        )

    def __process_choice(self, widget: Question_MultipleChoice, prev_task_name: str):
        choices = []
        for ch in widget.answers:
            next_widget = self.widgets[ch.next_widget]
            choices.append(
                {
                    "Variable": f"$.results.{prev_task_name}.select",
                    "NumericEquals": ch.number,
                    "Next": next_widget.name,
                }
            )

        return Choice(
            Choices=choices
        )

    def __widget_steps(self):
        for key, curr_widget in self.widgets.items():
            next_widget_id = curr_widget.next_widget
            next_widget = self.widgets[next_widget_id] if next_widget_id else None

            if isinstance(curr_widget, Question_MultipleChoice):
                choice = self.__process_choice(curr_widget, curr_widget.name)
                self.sm.States[curr_widget.name + "choice"] = choice
                task = self.__create_step_from_widget(curr_widget, curr_widget)
                task.Next = curr_widget.name + "choice"

            else:
                task = self.__create_step_from_widget(curr_widget, next_widget)

            self.sm.States[curr_widget.name] = task

    def __create_step_from_widget(self, widget: DbWidget, next_widget: DbWidget = None):
        next_task_name = self.FINISH_STEP_NAME
        if next_widget:
            next_task_name = next_widget.name

        return self.__process_task(widget, next_task_name)

    def __process_task(self, widget: DbWidget, next_task_name: str):
        widget_class_name = type(widget).__name__
        tasks = QUESTION_CELERY_TASKS[widget_class_name]
        return Task(
            Resource=self.TASK_RESOURCE__LAMBDA_WAIT_FOR_TOKEN,
            Next=next_task_name,
            ResultPath=f"$.results.{widget.name}",
            Parameters={
                "FunctionName": self.lambda_celery_client_arn,
                "Payload": {
                    "taskName": tasks["prompt"],
                    "workspace.$": "$.input.workspace",
                    "carePlanAssignmentId.$": "$.input.carePlanAssignmentId",
                    "widgetId": widget.id,
                    "taskToken.$": "$$.Task.Token"
                }
            }
        )
