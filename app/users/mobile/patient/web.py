from fastapi import Depends, File, Request, UploadFile

import app.users.common.models.db as users_common_dbm
import app.users.common.models.web as users_common_wbm
from app.context import get_current_workspace
from app.tenant_workspaces.model_db import Workspace
from core.errors import HTTPNotFoundError
from web.cloudauth.auth_claims import AuthClaims
from web.cloudauth.auth_current_user import AuthCurrentUser
from .logic.photo import upload_patient_photo
from .router import router_patient
from .web_model import MobileProfilePhotoUploadResult

get_current_user = AuthCurrentUser()


@router_patient.post("/photo", response_model=MobileProfilePhotoUploadResult)
async def mobile_patient_photo_upload(request: Request, file_: UploadFile = File(...),
                                      current_user: AuthClaims = Depends(get_current_user)):
    """ 1. Create folder in AWS S3 for patient if not exist yet
    2. Save file photo to AWS S3
    3. Save file path in DB in patient profile if exist
    4. Return full path to new photo (ID needed?)"""
    workspace: Workspace = await get_current_workspace(request)

    return await upload_patient_photo(workspace, file_, current_user)


@router_patient.get("/info", response_model=users_common_wbm.PatientUserInfo)
async def get_mobile_patient_info(request: Request,
                                  current_user: AuthClaims = Depends(get_current_user)):
    patient: users_common_dbm.PatientUser = users_common_dbm.PatientUser.objects(
        cognito_sub=current_user.sub).first()
    if not patient:
        raise HTTPNotFoundError(message=f"Patient not found [{current_user.sub}]")

    return users_common_wbm.PatientUserInfo(
        id=patient.id,
        firstName=patient.firstName,
        lastName=patient.lastName,
        email=patient.email,
        phone=patient.phone,
        birthDate=patient.birthDate,
        photo=patient.photo,
        photoContentType=patient.photo_content_type,
    )


@router_patient.put("/info", response_model={},
                    response_description="Patient info successfully updated")
async def update_mobile_patient_info(web_object: users_common_wbm.PatientUserUpdate,
                                     request: Request,
                                     current_user: AuthClaims = Depends(get_current_user)):
    db_patient: users_common_dbm.PatientUser = users_common_dbm.PatientUser.objects(
        cognito_sub=current_user.sub).first()
    if not db_patient:
        raise HTTPNotFoundError(message=f"Patient not found [{current_user.sub}]")

    db_patient.firstName = web_object.firstName
    db_patient.lastName = web_object.lastName
    db_patient.birthDate = web_object.birthDate
    db_patient.sex = web_object.sex
    db_patient.save()
    return {}
