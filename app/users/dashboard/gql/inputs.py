import graphene

from app.models.gql import AddressInput
from app.users.common.models.gql.role import RoleEnum
from app.users.common.models.gql.sex import SexEnum
from app.users.common.models.gql.user_dashboard import SpecialityEnum


class UserByEmailInput(graphene.InputObjectType):
    email = graphene.String(required=True)
    sendEmail = graphene.Boolean(default_value=False)


class UserByPhoneInput(graphene.InputObjectType):
    phone = graphene.String(required=True)
    sendSms = graphene.Boolean(default_value=False)


class UserInput(graphene.InputObjectType):
    firstName = graphene.String(required=True)
    lastName = graphene.String(required=True)

    byPhone = graphene.InputField(UserByPhoneInput)
    byEmail = graphene.InputField(UserByEmailInput)

    @property
    def email(self):
        if self.byEmail:
            return self.byEmail.email

        else:
            return ""

    @email.setter
    def email(self, value):
        self.byEmail.email = value

    @property
    def phone(self):
        if self.byPhone:
            return self.byPhone.phone

        else:
            return ""

    @phone.setter
    def phone(self, value):
        self.byPhone.phone = value

    @property
    def send_sms(self):
        if self.byPhone:
            return self.byPhone.sendSms

        else:
            return False

    @send_sms.setter
    def send_sms(self, value):
        self.byPhone.sendSms = value

    @property
    def send_email(self):
        if self.byEmail:
            return self.byEmail.sendEmail

        else:
            return False

    @send_email.setter
    def send_email(self, value):
        self.byEmail.sendEmail = value


class PatientUserInput(UserInput):
    birthDate = graphene.Date(required=True)
    sex = SexEnum(required=True)


class PatientUpdateInput(graphene.InputObjectType):
    id_ = graphene.ID(required=True)
    firstName = graphene.String()
    lastName = graphene.String()
    address = graphene.InputField(AddressInput)
    birthDate = graphene.Date()
    sex = SexEnum()
    language = graphene.String()


class DashboardUserUpdateMeInput(graphene.InputObjectType):
    firstName = graphene.String()
    lastName = graphene.String()
    address = graphene.InputField(AddressInput)
    birthDate = graphene.Date()
    sex = SexEnum()
    language = graphene.String()

    status = graphene.String()
    speciality = SpecialityEnum()
    description = graphene.String()
    title = graphene.String()


class DashboardUserUpdateInput(graphene.InputObjectType):
    firstName = graphene.String()
    lastName = graphene.String()
    org_unit = graphene.ID()
    role = RoleEnum()


class DashboardUserInput(UserInput):
    orgUnitId = graphene.ID()
    role = RoleEnum(required=True)


class FilterFindManyPatientInput(graphene.InputObjectType):
    start_age = graphene.Int()
    end_age = graphene.Int()
    gender = graphene.List(SexEnum)
    name = graphene.String()
    location = graphene.String()
    care_team_id = graphene.ID()
    sub_org_id = graphene.ID()
    email = graphene.String()
    medical_condition_index = graphene.ID()


class FilterFindManyUserInput(graphene.InputObjectType):
    role = RoleEnum()
    name = graphene.String()
    care_team_id = graphene.ID(name="careTeam")
    sub_org_id = graphene.ID(name="subOrg")
    is_free = graphene.Boolean()
    email = graphene.String()
