import collections
import json
from typing import Any, Dict, List, Optional, OrderedDict

from bson import ObjectId
from pydantic import BaseModel, Field

import core.aws.client


class AwsStepFunctions:

    def __init__(self, aws_region: str):
        self.client = core.aws.client.get_step_functions(aws_region)

    def create_state_machine(self, name="", definition="", role_arn=""):
        try:
            return self.client.create_state_machine(name=name, definition=definition,
                                                    roleArn=role_arn)
        except:
            raise

    def start_execution(self, state_machine_arn: str = "", input_=None):
        if input_ is None:
            input_ = {}
        try:
            return self.client.start_execution(stateMachineArn=state_machine_arn,
                                               input=json.dumps(input_))
        except:
            raise

    def send_task_success(self, task_token, output=None, **kwargs):
        if output is None:
            output = {
                "success": True,
                "message": "Callback Success"
            }

        for key, value in kwargs.items():
            output[key] = value

        try:
            return self.client.send_task_success(
                taskToken=task_token,
                output=json.dumps(output)
            )
        except:
            raise

    def send_choice_success(self, task_token, select: int, output=None, **kwargs):
        if output is None:
            output = {
                "success": True,
                "message": "Callback Success",
                "select": select,
            }

        for key, value in kwargs.items():
            output[key] = value

        try:
            return self.client.send_task_success(
                taskToken=task_token,
                output=json.dumps(output)
            )
        except:
            raise

class State(BaseModel):
    # Name: str = Field(alias="Name")
    Type: str = Field(alias="Type")
    Comment: Optional[str] = Field(alias="Comment")
    InputPath: Optional[str] = Field(alias="InputPath")
    OutputPath: Optional[str] = Field(alias="OutputPath")
    Next: Optional[str] = Field(alias="Next")
    End: Optional[bool] = Field(alias="End")

    class Config:
        json_encoders = {
            ObjectId: lambda v: str(v),
        }


class Pass(State):
    Type: str = Field("Pass")
    Result: Optional[Any] = Field(alias="Result")
    ResultPath: Optional[Any] = Field(alias="ResultPath")
    Parameters: Optional[Dict] = Field(alias="Parameters")


class Task(State):
    Type: str = Field("Task")
    Resource: Optional[str] = Field(alias="Resource")
    Parameters: Optional[Dict] = Field(alias="Parameters")
    ResultPath: Optional[Any] = Field(alias="ResultPath")
    ResultSelector: Optional[Any] = Field(alias="ResultSelector")
    Retry: Optional[Dict] = Field(alias="Retry")
    Catch: Optional[Dict] = Field(alias="Catch")
    TimeoutSeconds: Optional[int] = Field(alias="TimeoutSeconds")
    TimeoutSecondsPath: Optional[str] = Field(alias="TimeoutSecondsPath")
    HeartbeatSeconds: Optional[int] = Field(alias="HeartbeatSeconds")
    HeartbeatSecondsPath: Optional[str] = Field(alias="HeartbeatSecondsPath")


class Choice(State):
    Type: str = Field("Choice")
    Choices: Optional[List[Dict]] = Field(alias="Choices")
    Default: Optional[str] = Field(alias="Default")


class Wait(State):
    Type: str = Field("Wait")
    Seconds: Optional[int] = Field(alias="Seconds")
    Timestamp: Optional[str] = Field(alias="Timestamp")
    SecondsPath: Optional[str] = Field(alias="SecondsPath")
    TimestampPath: Optional[str] = Field(alias="TimestampPath")


class Succeed(State):
    Type: str = Field("Succeed")


class Fail(State):
    Type: str = Field("Fail")
    Cause: Optional[str] = Field(alias="Cause")
    Error: Optional[str] = Field(alias="Error")


class Parallel(State):
    Type: str = Field("Parallel")


class Map(State):
    Type: str = Field("Map")


class StateMachine(BaseModel):
    Version: Optional[str] = Field("1.0", alias="Version")
    Comment: Optional[str] = Field(alias="Comment")
    StartAt: str = Field(alias="StartAt")
    TimeoutSeconds: Optional[int] = Field(alias="TimeoutSeconds")
    States: OrderedDict[str, State] = Field(collections.OrderedDict(), alias="States")

    class Config:
        json_encoders = {
            ObjectId: lambda v: str(v),
        }
