from typing import List

from app.org_units.model_db import OrgUnit
from app.users.common.models.db import DashboardUser as User, PatientUser as Patient
from ...model_web import CareTeamMember, CareTeamMembers, CareTeams


async def get_care_team_and_members(current_user) -> CareTeams:
    patient: Patient = Patient.objects.filter(cognito_sub=current_user.sub).first()
    if patient.orgUnitId:
        care_team: OrgUnit = OrgUnit.objects.with_id(patient.orgUnitId)

        if not care_team:
            return CareTeams()
    else:
        return CareTeams()

    users = User.objects.filter(orgUnitId=care_team.id).all()
    web_users = map_users(users)

    care_team_members = CareTeamMembers(members=web_users,
                                        careTeamId=str(care_team.id), )

    return CareTeams(
        careTeamMembers=[care_team_members]
    )


def map_users(users: List[User]) -> List[CareTeamMember]:
    web_users = []
    for user in users:
        web_user = CareTeamMember(
            id=str(user.id),
            role=user.role,
            firstName=user.firstName,
            lastName=user.lastName,
            speciality=user.speciality,
            avatar=user.photo
        )

        web_users.append(web_user)

    return web_users
