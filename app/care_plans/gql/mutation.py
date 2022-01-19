import json
from datetime import datetime

import graphene

from app.context import get_current_workspace, get_user
from app.users.common.models.db import PatientUser as Patient
from app.users.common.models.gql import PatientUser as GqlPatient
from core.aws.sfn import AwsStepFunctions
from core.config import get_app_config
from core.errors import NotFoundGqlError
from core.factory.celery import get_celery_app
from core.logic.base_payload import MutationPayload
from ..gql.inputs import CarePlanInput
from ..logic.state_machine_generator import AwsStateMachineGenerator
from ..logic.widgets_generator import process_json, save
from ..models.care_plan_db import CarePlanAssignment, DbCarePlan, DbCarePlanStatus
from ..models.gql import GqlCarePlan, GqlCarePlanType

celery_app = get_celery_app()
cfg = get_app_config()


class CreateCarePlan(MutationPayload):
    """
        Create new care plan.

        revision is being set to 1 and then autoincremented on further updates
        status is DRAFT. It can be changed by calling Publish
    """

    class Arguments:
        type_ = graphene.Argument(GqlCarePlanType, name="type", required=True)
        data = CarePlanInput(required=True)

    result_id = graphene.ID()
    result = graphene.Field(GqlCarePlan)

    async def mutate(self, info, type_: GqlCarePlanType, data: CarePlanInput):
        author = await get_user(info)

        dbo: DbCarePlan = DbCarePlan.from_gql(data, author.id, )
        dbo.save()

        return CreateCarePlan(result_id=dbo.id, result=GqlCarePlan.from_db(dbo))


class UpdateCarePlan(MutationPayload):
    class Arguments:
        type_ = graphene.Argument(GqlCarePlanType, name="type", required=True)
        data = CarePlanInput(required=True)

    result_id = graphene.ID()
    result = graphene.Field(GqlCarePlan)

    async def mutate(self, info, type_: GqlCarePlanType, data: CarePlanInput):
        author = await get_user(info)

        dbo: DbCarePlan = DbCarePlan.objects().with_id(data.id_)

        if not dbo.author_id:
            dbo.author_id = str(author.id)

        if data.name:
            dbo.name = data.name
        if data.subtitle:
            dbo.subtitle = data.subtitle
        if data.description:
            dbo.description = data.description
        if data.image:
            dbo.image = data.image

        if data.duration_months:
            dbo.duration_months = data.duration_months
        if data.duration_weeks:
            dbo.duration_weeks = data.duration_weeks
        if data.duration_days:
            dbo.duration_days = data.duration_days

        if data.tags:
            dbo.tags = data.tags

        dbo.revision = dbo.revision + 1

        dbo.save()
        return UpdateCarePlan(result_id=dbo.id, result=GqlCarePlan.from_db(dbo))


class PublishCarePlan(MutationPayload):
    class Arguments:
        type_ = graphene.Argument(GqlCarePlanType, name="type", required=True)
        id_ = graphene.ID()

    async def mutate(self, info, type_: GqlCarePlanType, id_: graphene.ID()):
        dbo: DbCarePlan = DbCarePlan.objects().with_id(id_)
        dbo.status = DbCarePlanStatus.PUBLISHED
        dbo.save()
        return PublishCarePlan(ok=True)


class CloneCarePlan(MutationPayload):
    class Arguments:
        type_ = graphene.Argument(GqlCarePlanType, name="type", required=True)
        id_ = graphene.ID()

    async def mutate(self, info, type_: GqlCarePlanType, id_: graphene.ID()):
        # dbo_source: DbCarePlan = DbCarePlan.objects().with_id(id_)

        # TODO: implement
        # bo.save()
        return CloneCarePlan(ok=True)


class LoadJsonCarePlan(MutationPayload):
    class Arguments:
        type_ = graphene.Argument(GqlCarePlanType, name="type", required=True)
        id_ = graphene.ID()
        ui_json = graphene.String()

    result_id = graphene.ID()
    result = graphene.Field(GqlCarePlan)

    async def mutate(self, info, type_: GqlCarePlanType, id_: graphene.ID(), ui_json: str):
        db: DbCarePlan = DbCarePlan.objects().with_id(id_)
        db.ui_json = ui_json

        import traceback

        try:
            ui_json = json.loads(ui_json).get("graph")
            print("LOG CAREPLAN UI_JSON ", ui_json)
            
            widgets = process_json(ui_json, id_)
            save(list(widgets.values()))
            
            sf_gen = AwsStateMachineGenerator(db, widgets, cfg.AWS_LAMBDA_CELERY_CLIENT)
            sf_json = sf_gen.care_plan_to_json()
            print(sf_json)
            
            sf = AwsStepFunctions("eu-west-3")
            res = sf.create_state_machine(db.name.replace(" ", "") + str(datetime.now().timestamp()),
                                        sf_json, cfg.AWS_STEP_FUNCTION_ROLE_ARN)
            db.aws_state_machine_arn = res.get("stateMachineArn")
            db.creation_date = res.get("creationDate")
            print(res)

        except Exception as e: 
            print(e)
            print("")
            traceback.print_exc()

        db.save()
        return LoadJsonCarePlan(result_id=db.id, result=GqlCarePlan.from_db(db))


class DeleteCarePlan(MutationPayload):
    class Arguments:
        type_ = graphene.Argument(GqlCarePlanType, name="type", required=True)
        id_ = graphene.ID()

    async def mutate(self, info, type_: GqlCarePlanType, id_: graphene.ID()):
        # TODO delete_handler(id_)
        return DeleteCarePlan(ok=True)


class RunCarePlan(MutationPayload):
    class Arguments:
        care_plan_id = graphene.ID(required=True)
        patient_id = graphene.ID(required=True)

    assignment_id = graphene.ID()
    patient = graphene.Field(GqlPatient)

    async def mutate(self, info, care_plan_id: str, patient_id: str):
        cp = DbCarePlan.objects.with_id(care_plan_id)
        if not cp:
            return RunCarePlan(error=NotFoundGqlError())

        patient = Patient.objects.with_id(patient_id)
        workspace = await get_current_workspace(info.context["request"])

        cp_as = CarePlanAssignment()
        cp_as.care_plan_id = care_plan_id
        cp_as.patient_id = patient_id
        cp_as.save()

        celery_app.send_task("care_plans.start",
                             kwargs={
                                 "workspace": workspace.short_name,
                                 "care_plan_assignment_id": str(cp_as.id),
                             })

        return RunCarePlan(assignment_id=cp_as.id, patient=GqlPatient.from_db(patient))


class IsRunCarePlan(MutationPayload):
    class Arguments:
        assignment_id = graphene.ID()

    status = graphene.Boolean()

    async def mutate(self, _, assignment_id: str):
        cp_as: CarePlanAssignment = CarePlanAssignment.objects.with_id(assignment_id)
        if not cp_as:
            return RunCarePlan(error=NotFoundGqlError())

        return RunCarePlan(status=bool(cp_as.aws_execution_id))


class RunCarePlans(MutationPayload):
    """Run care plans by medical condition index for all patient in dashboard user's care team"""

    class Arguments:
        care_plan_id = graphene.ID(required=True)
        medical_condition_index = graphene.ID(required=True)

    async def mutate(self, info, care_plan_id: str, medical_condition_index: str):
        cp = DbCarePlan.objects.with_id(care_plan_id)
        if not cp:
            return RunCarePlan(error=NotFoundGqlError())

        user = await get_user(info)
        workspace = await get_current_workspace(info.context["request"])
        patients = Patient.objects.filter(
            deleted=False,
            orgUnitId=user.orgUnitId,
            medical_condtions__index=medical_condition_index,
        ).all()

        for patient in patients:
            cp_as = CarePlanAssignment()
            cp_as.care_plan_id = care_plan_id
            cp_as.patient_id = patient.id
            cp_as.save()

            celery_app.send_task("care_plans.start",
                                 kwargs={
                                     "workspace": workspace.short_name,
                                     "care_plan_assignment_id": str(cp_as.id),
                                 })

        return RunCarePlans()


class CarePlanMutations(graphene.Mutation):
    create = CreateCarePlan.Field()
    update = UpdateCarePlan.Field()
    publish = PublishCarePlan.Field()
    clone = CloneCarePlan.Field()
    delete = DeleteCarePlan.Field()
    run_care_plan = RunCarePlan.Field()
    run_care_plans = RunCarePlans.Field()
    is_run = IsRunCarePlan.Field()
    load_json = LoadJsonCarePlan.Field()

    async def mutate(self, _):
        return {}
