import graphene

from app.context import get_current_auth
from app.models.db.address import Address
from app.users.common.models.db import DashboardUser, PatientUser as DbPatientUser
from app.users.common.models.gql import PatientUser as GqlPatientUser
from core.errors import NotFoundGqlError, TitleAlreadyTakenGqlError, ValidationGqlError
from core.logic.base_payload import MutationPayload

from app.patient_info.allergy.gql.mutations import AllergyMutations
from app.patient_info.lifestyle.gql.mutations import LifestyleMutations
from app.patient_info.vaccine.gql.mutations import VaccineMutations
from app.patient_info.family.gql.mutations import UpdateFamily

from ..inputs import PatientUpdateInput, PatientUserInput
from app.users.dashboard.logic.patient.create import create_patient_handler
from app.users.dashboard.logic.patient.delete import delete_patient_handler
from ..utils import is_email_exist, is_empty, is_phone_exist


class CreatePatientUser(MutationPayload):
    """Mutation to create user patient."""

    class Arguments:
        record = PatientUserInput(required=True)

    result = graphene.Field(GqlPatientUser)
    result_id = graphene.ID()

    async def mutate(self, info, record):

        # TODO check is authenticated and permission for create
        # if not info.context.user.is_authenticated:
        #    errors.append(NotAuthenticated(...))

        if not CreatePatientUser._is_exist_contacts(record):
            error = ValidationGqlError(
                message="`byEmail.email` or `byPhone.phone` fields must not be empty")
            return CreatePatientUser(error=error)

        if CreatePatientUser._is_email_exist_in_db(record):
            error = TitleAlreadyTakenGqlError(message="Email already taken", path="byEmail.email")
            return CreatePatientUser(error=error)

        if CreatePatientUser._is_phone_exist_in_db(record):
            error = TitleAlreadyTakenGqlError(message="Phone already taken", path="byPhone.phone")
            return CreatePatientUser(error=error)

        try:
            request = info.context["request"]
            auth = await get_current_auth(request)
            user = DashboardUser.objects(cognito_sub=auth.sub).first()

            patient = await create_patient_handler(record, request)
            patient.orgUnitId = user.orgUnitId
            patient.save()
            return CreatePatientUser(result_id=patient.id, result=GqlPatientUser.from_db(patient))
        except Exception as e:
            if hasattr(e, "response") and e.response["Error"]["Code"] == "UsernameExistsException":
                error = TitleAlreadyTakenGqlError(message="Username already taken")
                return CreatePatientUser(error=error)
            else:
                raise

    @staticmethod
    def _is_exist_contacts(record) -> bool:
        return bool(record.byEmail or record.byPhone)

    @staticmethod
    def _is_email_exist_in_db(record) -> bool:
        if not record.byEmail:
            return False
        else:
            return not is_empty(record.byEmail.email) and is_email_exist(
                email=record.byEmail.email, user_collection=DbPatientUser
            )

    @staticmethod
    def _is_phone_exist_in_db(record) -> bool:
        if not record.byPhone:
            return False
        return not is_empty(record.byPhone.phone) and is_phone_exist(
            phone=record.byPhone.phone, user_collection=DbPatientUser
        )


class UpdatePatient(MutationPayload):
    """Mutation to update basic patient information."""

    class Arguments:
        record = PatientUpdateInput(required=True)

    result_id = graphene.ID()
    result = graphene.Field(GqlPatientUser)

    async def mutate(self, _, record: PatientUpdateInput):

        # TODO check is authenticated and permission for update
        # if not info.context.user.is_authenticated:
        #    errors.append(NotAuthenticated(...))

        patient = DbPatientUser.objects(pk=record.id_).first()
        if not patient:
            error = NotFoundGqlError(message="Patient-user is not found by id")
            return UpdatePatient(error=error)

        UpdatePatient._update_patient(patient, record)

        return UpdatePatient(result_id=patient.id, result=GqlPatientUser.from_db(patient))

    @staticmethod
    def _update_patient(user_db: DbPatientUser, record: PatientUpdateInput):
        if record.firstName:
            user_db.firstName = record.firstName
        if record.lastName:
            user_db.lastName = record.lastName
        if record.address:
            user_db.address = Address.from_gql(record.address)
        if record.birthDate:
            user_db.birthDate = record.birthDate
        if record.sex:
            user_db.sex = record.sex
        if record.language:
            user_db.language = record.language

        user_db.save()


class DeletePatient(MutationPayload):
    """Mutation to delete patient by id."""

    class Arguments:
        id_ = graphene.ID(required=True)

    async def mutate(self, info, id_):
        await delete_patient_handler(id_, info.context["request"])

        return DeletePatient()


class PatientUserMutations(graphene.Mutation):
    """Patient user mutations."""
    create = CreatePatientUser.Field()
    update = UpdatePatient.Field()
    delete = DeletePatient.Field()

    update_family = UpdateFamily.Field()

    allergy = AllergyMutations.Field()
    vaccine = VaccineMutations.Field()
    lifestyle = LifestyleMutations.Field()

    async def mutate(self, _):
        return {}
