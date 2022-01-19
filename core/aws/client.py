import boto3

from core.config import get_app_config


def get_boto3_client(client: str, aws_region: str):
    cfg = get_app_config()
    return boto3.client(
        client,
        region_name=aws_region,
        aws_access_key_id=cfg.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=cfg.AWS_SECRET_ACCESS_KEY,
    )


def get_cognito_idp(aws_region: str = "eu-west-1"):
    return get_boto3_client("cognito-idp", aws_region)


def get_ses(aws_region: str = "eu-west-1"):
    return get_boto3_client("ses", aws_region)


def get_sns(aws_region: str = "eu-west-1"):
    return get_boto3_client("sns", aws_region)


def get_kinesis(aws_region: str = "eu-west-1"):
    return get_boto3_client("kinesis", aws_region)


def get_step_functions(aws_region: str):
    return get_boto3_client("stepfunctions", aws_region)


def get_boto3_resource(resource: str, aws_region: str = "eu-west-1"):
    cfg = get_app_config()
    return boto3.resource(
        resource,
        region_name=aws_region,
        aws_access_key_id=cfg.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=cfg.AWS_SECRET_ACCESS_KEY,
    )
