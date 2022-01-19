import os

from fastapi import UploadFile

import app.users.common.models.db as users_common_dbm
from app.tenant_workspaces.model_db import Workspace
from core.config import get_app_config
from core.errors import HTTPNotFoundError
from core.utils.aws import get_boto3_resource
from core.utils.transaction import Transaction
from web.cloudauth.auth_claims import AuthClaims
from web.cloudauth.auth_current_user import AuthCurrentUser
from ..web_model import MobileProfilePhotoUploadResult

get_current_user = AuthCurrentUser()
cfg = get_app_config()


async def upload_patient_photo(workspace: Workspace, file: UploadFile, current_user: AuthClaims):
    print("[PATIENT-UPLOAD-PHOTO] Start")
    patient: users_common_dbm.PatientUser = users_common_dbm.PatientUser.objects(
        cognito_sub=current_user.sub).first()
    if not patient:
        raise HTTPNotFoundError(message=f"Patient not found [{current_user.sub}]")
    filename, file_extension = os.path.splitext(file.filename)

    print(filename)
    print(file_extension)
    bucket = __get_bucket(workspace.s3.name, workspace.s3.aws_region)
    key = f"patient/{patient.id}/profile_photo{file_extension}"

    with Transaction("MobileUploadPatientPhoto") as trx:
        data = await file.read()
        file_s3_path = __upload_patient_photo_to_s3(data, bucket, key, file.content_type,
                                                    workspace.s3.aws_region, workspace.s3.name, trx)
        __save_to_profile(patient, file_s3_path, file.content_type)

        trx.commitAll()
        return MobileProfilePhotoUploadResult(status="OK", url=file_s3_path)


def __upload_patient_photo_to_s3(file_, bucket_, key_, content_type, bucket_region, bucket_name,
                                 trx: Transaction):
    print("[PATIENT-UPLOAD-PHOTO] To AWS S3")

    response = bucket_.put_object(
        Body=file_,
        Key=key_,
        ContentType=content_type
    )
    trx.push(__rollback_upload, key_)

    return f"https://{bucket_name}.s3-{bucket_region}.amazonaws.com/{key_}"


def __rollback_upload(file_, patient_id):
    # TODO
    print("[PATIENT-UPLOAD-PHOTO-ROLLBACK] DB Patient")


def __rollback_save(db_object: users_common_dbm.PatientUser):
    # TODO
    print("[PATIENT-SAVE-PHOTO-ROLLBACK] DB Patient")


def __save_to_profile(patient: users_common_dbm.PatientUser, file_s3_path, content_type):
    patient.photo = file_s3_path
    patient.photo_content_type = content_type
    patient.save()


def __get_bucket(bucket_name, bucket_region):
    s3_resource = get_boto3_resource("s3", bucket_region)
    return s3_resource.Bucket(bucket_name)
