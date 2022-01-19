import os

import dotenv

dotenv.load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

ENVIRONMENT_NAME = None  # This is used in naming your Cognito user pools.


def init_config():
    global ENVIRONMENT_NAME
    ENVIRONMENT_NAME = os.getenv("ENVIRONMENT_NAME")
    print("[APP] Loaded configuration from .env file.")
    print(f"[APP] ENVIRONMENT_NAME: {ENVIRONMENT_NAME}")


class Config:
    CORS_ORIGINS = "[\"*\"]"
    ENVIRONMENT_NAME = os.getenv("ENVIRONMENT_NAME")
    MASTER_DB_CONNECTION = os.getenv("MASTER_DB_CONNECTION")

    # AWS Settings
    AWS_REGION_NAME = "eu-west-1"
    SENDER_EMAIL = os.getenv("SENDER_EMAIL")
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_STEP_FUNCTION_ROLE_ARN = os.getenv("AWS_STEP_FUNCTION_ROLE_ARN")
    AWS_LAMBDA_CELERY_CLIENT = os.getenv("AWS_LAMBDA_CELERY_CLIENT")

    # SENDBIRD API TOKEN
    SENDBIRD_SYSTEM_ACCOUNT = os.getenv("SENDBIRD_SYSTEM_ACCOUNT")
    SENDBIRD_ORGANIZATION_API_TOKEN = os.getenv("SENDBIRD_ORGANIZATION_API_TOKEN")

    # CELERY
    CELERY_RABBITMQ_URL = os.getenv("CELERY_RABBITMQ_URL")
    CELERY_BACKEND_URL = os.getenv("CELERY_BACKEND_URL")


def get_app_config():
    return Config()


init_config()
