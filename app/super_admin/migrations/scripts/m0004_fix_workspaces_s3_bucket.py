import json

from app.tenant_workspaces.model_db import Workspace as DbWorkspace, WorkspaceS3Bucket
from core.config import get_app_config
from core.utils.aws import get_s3


async def run():
    cfg = get_app_config()

    log = []
    for obj in DbWorkspace.objects():
        wks: DbWorkspace = obj
        s3_bucket: WorkspaceS3Bucket = wks.s3
        if s3_bucket.aws_region:
            continue

        region = wks.aws_region
        bucket_name = f"{cfg.ENVIRONMENT_NAME}-{wks.short_name}"
        s3_client = get_s3(region)

        location = {'LocationConstraint': region}
        s3_client.create_bucket(Bucket=bucket_name,
                                ACL="public-read",
                                CreateBucketConfiguration=location)
        bucket_policy = {
            'Version': '2012-10-17',
            'Statement': [{
                'Sid': 'AddPerm',
                'Effect': 'Allow',
                'Principal': '*',
                'Action': ['s3:GetObject'],
                'Resource': f"arn:aws:s3:::{bucket_name}/*"
            }]
        }
        bucket_policy = json.dumps(bucket_policy)
        s3_client.put_bucket_policy(Bucket=bucket_name, Policy=bucket_policy)
        log.append(bucket_name)
        log.append(region)

        db_s3 = WorkspaceS3Bucket()
        db_s3.aws_region = region
        db_s3.name = bucket_name
        wks.s3 = db_s3

        wks.save()

    return log
