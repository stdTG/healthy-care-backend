from fastapi import Depends

import app.settings.models.web as webm
from web.cloudauth.auth_claims import AuthClaims
from web.cloudauth.auth_current_user import AuthCurrentUser
from .logic import get_patient_settings_handler, set_patient_settings_handler
from .router import router_mobile

get_current_user = AuthCurrentUser()


@router_mobile.get("/", response_model=webm.PatientSettings)
async def get_patient_settings(current_user: AuthClaims = Depends(get_current_user)):
    return await get_patient_settings_handler.run(current_user.sub)


@router_mobile.post("/", )
async def set_patient_settings(web_object: webm.PatientSettings,
                               current_user: AuthClaims = Depends(get_current_user)):
    await set_patient_settings_handler.run(web_object, current_user.sub)
    return {}
