import uuid

import core.aws.sfn as sfn
import app.care_plans.models.care_plan_db as cpd
import app.care_plans.logic.converter as cpv

from core.config import get_app_config
from app.context import get_public_workspace_by_short_name
from core.utils.db import register_master_connection, register_tenant_connection

cfg = get_app_config()
register_master_connection(cfg)
wks = get_public_workspace_by_short_name("ignilife")

client = sfn.AwsStepFunctions("eu-west-3")

stateMachineName = f"Test_State_Machine_{uuid.uuid4().hex}"
definition = """
{
   "Comment": "STATE_MACHINE_NAME",
   "StartAt": "Startup",
   "States": {
     "Startup": {
       "Type": "Task",
       "Resource": "arn:aws:states:::lambda:invoke.waitForTaskToken",
       "TimeoutSeconds": 100,
       "Parameters": {
         "FunctionName": "arn:aws:lambda:eu-west-3:673544484741:function:alakine-celery-client:$LATEST",
         "Payload": {
           "taskName": "care_plans.question.text_prompt",
           "workspace.$": "$.input.workspace",
           "carePlanId.$": "$.input.carePlanId",
           "widgetId.$": "$.input.widgetId",
           "taskToken.$": "$$.Task.Token"
         }
       },
       "ResultPath": null,
       "Next": "Question_Text1"
     },
     "Question_Text1": {
       "Type": "Task",
       "Resource": "arn:aws:states:::lambda:invoke.waitForTaskToken",
       "TimeoutSeconds": 100,
       "Parameters": {
         "FunctionName": "arn:aws:lambda:eu-west-3:673544484741:function:alakine-celery-client:$LATEST",
         "Payload": {
           "taskName": "care_plans.question.text_prompt",
           "workspace.$": "$.input.workspace",
           "carePlanId.$": "$.input.carePlanId",
           "widgetId.$": "$.input.widgetId",
           "taskToken.$": "$$.Task.Token"
         }
       },
       "ResultPath": null,
       "Next": "Question_YesNo1"
     },
     "Question_YesNo1": {
       "Type": "Task",
       "Resource": "arn:aws:states:::lambda:invoke.waitForTaskToken",
       "TimeoutSeconds": 100,
       "Parameters": {
         "FunctionName": "arn:aws:lambda:eu-west-3:673544484741:function:alakine-celery-client:$LATEST",
         "Payload": {
           "taskName": "care_plans.question.yes_no_prompt",
           "workspace.$": "$.input.workspace",
           "carePlanId.$": "$.input.carePlanId",
           "widgetId.$": "$.input.widgetId",
           "taskToken.$": "$$.Task.Token"
         }
       },
       "ResultPath": null,
       "Next": "Question_NumberSimple1"
     },
     "Question_NumberSimple1": {
       "Type": "Task",
       "Resource": "arn:aws:states:::lambda:invoke.waitForTaskToken",
       "TimeoutSeconds": 100,
       "Parameters": {
         "FunctionName": "arn:aws:lambda:eu-west-3:673544484741:function:alakine-celery-client:$LATEST",
         "Payload": {
           "taskName": "care_plans.question.number_simple_prompt",
           "workspace.$": "$.input.workspace",
           "carePlanId.$": "$.input.carePlanId",
           "widgetId.$": "$.input.widgetId",
           "taskToken.$": "$$.Task.Token"
         }
       },
       "ResultPath": null,
       "Next": "ShouldRepeat?"
     },
     "ShouldRepeat?": {
       "Type": "Choice",
       "Choices": [
         {
           "Variable": "$.input.repeat",
           "NumericEquals": 0,
           "Next": "Finish"
         }
       ],
       "Default": "WaitOneMinute"
     },
     "WaitOneMinute": {
       "Type": "Wait",
       "Seconds": 60,
       "Next": "Startup"
     },
     "Finish": {
       "Type": "Pass",
       "End": true
     }
   }
 }
"""

response = client.create_state_machine(name=stateMachineName, definition = definition, roleArn=wks.step_functions.iam_role_arn)
print(response)