from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..gql.inputs import CarePlanInput

from mongoengine import Document, DynamicField, EmbeddedDocument, signals
from mongoengine.fields import (ListField, ObjectIdField, StringField, DateTimeField, IntField,
                                BooleanField, URLField, )

from core.utils.str_enum import StrEnum


class DbCarePlanType(StrEnum):
    Workspace = "workspace"
    Template = "template"


class DbCarePlanStatus(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"


class WidgetStatus(StrEnum):
    AWAIT = "await"
    OK = "ok"


class Operation(StrEnum):
    ADD = "add"
    SUBSTRACT = "substract"
    MULTIPLY = "multiply"
    DIVIDE = "divide"


class DbCarePlan(Document):
    meta = {
        "db_alias": "tenant-db-basic-data",
        "collection": "care_plans",
        "strict": False
    }

    name = StringField(required=True)
    subtitle = StringField(default="")
    description = StringField(default="")
    image = StringField(default="")
    duration_months = IntField(default=0)
    duration_weeks = IntField(default=0)
    duration_days = IntField(default=0)
    author_id = ObjectIdField(required=True, default="")
    tags = ListField()

    revision = IntField(required=True, default=1)
    status = StringField(choices=DbCarePlanStatus, default=DbCarePlanStatus.DRAFT)

    deleted = BooleanField(default=False)
    ui_json = StringField(required=True, default="")

    aws_state_machine_arn = StringField(required=True, default="")
    creation_date = DateTimeField()

    @classmethod
    def from_gql(cls, gql: CarePlanInput, author_id: str, ) -> DbCarePlan:
        return cls(
            name=gql.name,
            subtitle=gql.subtitle,
            description=gql.description,

            duration_months=gql.duration_months,
            duration_weeks=gql.duration_weeks,
            duration_days=gql.duration_days,

            author_id=author_id,

            tags=gql.tags if gql.tags else [],
        )


def mongoengine_handler(event):
    """Signal decorator to allow use of callback functions as class decorators."""

    def decorator(fn):
        def apply(cls):
            event.connect(fn, sender=cls)
            return cls

        fn.apply = apply
        return fn

    return decorator


class Rule(EmbeddedDocument):
    equals = IntField()
    start = IntField()
    end = IntField()
    result_operate = StringField(choices=Operation)
    score = IntField()


class DbWidget(Document):
    meta = {
        "db_alias": "tenant-db-basic-data",
        "collection": "care_plan_widgets",
        "allow_inheritance": True,
        "strict": False
    }

    care_plan_id = ObjectIdField(required=True)
    name = StringField(required=True)

    current_widget = StringField(required=True)
    next_widget = StringField()
    is_start_widget = BooleanField(default=False)
    # scoreVarName = StringField()
    # scoreRules = ListField(Rule)
    deleted = BooleanField(default=False)


class Question(DbWidget):
    question_text = StringField(required=True)
    icon = StringField(required=True, default="default")
    metric_type = StringField(required=False, default="undefined")


@mongoengine_handler(signals.post_init)
def sample_post_init(sender, document):
    document.celeryTaskPrompt = "care_plan.question.sample_prompt"
    document.celeryTaskResponse = "care_plan.question.sample_response"


class CarePlanAssignment(Document):
    meta = {
        "db_alias": "tenant-db-basic-data",
        "collection": "care_plan_assignment",
        "strict": False
    }
    care_plan_id = ObjectIdField(required=True)
    patient_id = ObjectIdField(required=False)
    aws_execution_id = StringField(required=False)
    execution_start_date_time = DateTimeField(required=False)
    assigment_date_time = DateTimeField(required=False, default=lambda: datetime.now())


class WidgetPatientData(Document):
    meta = {
        "db_alias": "tenant-db-personal-data",
        "collection": "care_plan_widget_user_data",
        "allow_inheritance": True,
        "strict": False
    }

    widget_id = ObjectIdField(required=True, db_field="wId")
    aws_execution_id = StringField(required=False, db_field="awsExId")
    task_token = StringField(required=True, db_field="tkn")
    assignment_id = ObjectIdField(db_field="asid")
    data = DynamicField(db_field="dt")
    status = StringField(choices=WidgetStatus, db_field="st", default=str(WidgetStatus.AWAIT))
