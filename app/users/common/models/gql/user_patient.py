from __future__ import annotations

from typing import List, TYPE_CHECKING

from app.care_plans.gql.payloads import CarePlanAssignment
from app.care_plans.models.care_plan_db import DbCarePlan, CarePlanAssignment as DbCpAssignment
from app.care_plans.models.gql import GqlCarePlan

if TYPE_CHECKING:
    from ..db import PatientUser as DbPatientUser

import graphene

from app.models.gql import Address
from .sex import SexEnum
from .user import User, UserByPhone, UserByEmail
from app.patient_info.medical_history.models.gql import MedicalHistory
from app.patient_info.medical_history.models.db import MedicalHistory as DbMH
from app.patient_info.medical_condition.models.gql import MedicalConditionPatient

from app.patient_info.allergy.models.gql import Allergy
from app.patient_info.lifestyle.models.gql import Lifestyle
from app.patient_info.vaccine.models.gql import Vaccine
from app.patient_info.family.models.gql import Family


class PatientUser(User, graphene.ObjectType):
    sex = SexEnum(default_value=SexEnum.UNDEFINED)
    birthDate = graphene.Date()
    fullAddress = graphene.Field(Address)

    # patient data
    lifestyle = graphene.List(Lifestyle)
    vaccines = graphene.List(Vaccine)
    medical_history = graphene.List(lambda: MedicalHistory, default_value=[])
    medical_condition = graphene.List(lambda: MedicalConditionPatient, default_value=[])
    allergies = graphene.List(Allergy)
    family = graphene.Field(Family)
    assignments = graphene.List(CarePlanAssignment)

    @staticmethod
    async def resolve_medical_history(root, info):
        return [MedicalHistory.from_db(db) for db in DbMH.objects(patientId=root.id_).all()]


    @staticmethod
    async def resolve_assignments(root, _):
        assgns: List[DbCpAssignment] = DbCpAssignment.objects(patient_id=root.id_).all()
        cps: List[DbCarePlan] = DbCarePlan.objects(
            id__in=[asgn.care_plan_id for asgn in assgns]).all()
        cps_dict = {cp.id: cp for cp in cps}

        items = []
        for assgn in assgns:
            item = CarePlanAssignment()
            item.care_plan = GqlCarePlan.from_db(cps_dict[assgn.care_plan_id])
            item.assigment_date_time = assgn.assigment_date_time
            item.execution_start_date_time = assgn.execution_start_date_time

            items.append(item)

        return items

    @classmethod
    def from_db(cls, db: DbPatientUser) -> PatientUser:
        gql = cls(
            id_=db.id,
            firstName=db.firstName,
            lastName=db.lastName,
            birthDate=db.birthDate,
            language=db.language,
            sex=db.sex,
            lifestyle=db.lifestyle,
            vaccines=db.vaccines,
            family=Family(),
            allergies=db.allergies,
        )

        if db.phone:
            by_phone = UserByPhone()
            by_phone.phone = db.phone
            gql.byPhone = by_phone

        if db.email:
            by_email = UserByEmail()
            by_email.email = db.email
            gql.byEmail = by_email

        if db.address:
            gql.fullAddress = Address.from_db(db.address)

        if db.family:
            gql.family.mother = db.family.mother[0] if db.family.mother else None
            gql.family.father = db.family.father[0] if db.family.father else None
            gql.family.grandparents = db.family.grandparents[0] if db.family.grandparents else None

        if db.medical_conditions:
            gql.medical_condition = db.medical_conditions

        return gql
