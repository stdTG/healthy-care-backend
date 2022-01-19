from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models.care_plan_db import DbCarePlan

import graphene
from .care_plan_db import DbCarePlanStatus


class GqlCarePlanType(graphene.Enum):
    WORKSPACE = "workspace"
    TEMPLATE = "template"


class GqlCarePlanStatus(graphene.Enum):
    DRAFT = DbCarePlanStatus.DRAFT
    PUBLISHED = DbCarePlanStatus.PUBLISHED


class GqlCarePlan(graphene.ObjectType):
    id_ = graphene.ID()
    name = graphene.String(required=True, default_value="<untitled care plan>")
    subtitle = graphene.String(default_value="")
    description = graphene.String(required=True, default_value="")
    image = graphene.String(required=True, default_value="")
    duration_months = graphene.Int(default_value=0)
    duration_weeks = graphene.Int(default_value=0)
    duration_days = graphene.Int(default_value=0)
    author_id = graphene.ID()
    tags = graphene.List(graphene.String)

    revision = graphene.String(required=True, default_value=1)
    status = graphene.Field(GqlCarePlanStatus, default_value=GqlCarePlanStatus.DRAFT)

    deleted = graphene.Boolean(default_value=False)
    aws_state_machine_arn = graphene.String()
    ui_json = graphene.String()

    @classmethod
    def from_db(cls, db: DbCarePlan) -> GqlCarePlan:
        return cls(
            id_=db.id,
            name=db.name if db.name else "<untitled care plan>",
            subtitle=db.subtitle if db.subtitle else "",
            description=db.description,
            image=db.image,

            duration_months=db.duration_months,
            duration_weeks=db.duration_weeks,
            duration_days=db.duration_days,

            author_id=db.author_id,
            tags=db.tags,
            revision=db.revision,
            status=db.status,
            ui_json=db.ui_json,
        )

