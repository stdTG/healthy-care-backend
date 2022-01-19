from operator import itemgetter

from fastapi import Depends, Request

from app.context import get_current_master_org
from app.models.web import Address as WebAddress
from web.cloudauth.auth_claims import AuthClaims
from web.cloudauth.auth_current_user import AuthCurrentUser
from .router import router_mobile
from ..logic.mobile.care_team import get_care_team_and_members
from ..model_web import CareTeams, HealthCenter as WebHealthCenter, WorkingHours as WebWorkingHours

get_current_user = AuthCurrentUser()


@router_mobile.get("/health-center", response_model=WebHealthCenter)
async def get_info(request: Request):
    master_org = await get_current_master_org(request)

    web_working_hours = [WebWorkingHours.from_db(wh)
                         for wh in sorted(master_org.workingHours, key=itemgetter("dayOfWeek"))]

    return WebHealthCenter(
        id=str(master_org.id),
        title=master_org.name,
        description=master_org.description,
        address=WebAddress.from_db(master_org.address),
        schedule=web_working_hours,
        phone=master_org.phone,
        email=master_org.email,
    )


@router_mobile.get("/care-teams", response_model=CareTeams)
async def get_care_team_members(current_user: AuthClaims = Depends(get_current_user)):
    return await get_care_team_and_members(current_user)
