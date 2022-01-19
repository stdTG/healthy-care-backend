from collections import namedtuple

from core.config import get_app_config
from core.utils.aws import get_cognito_idp
from .user_pools_meta import SchemaAttributes

UserPool = namedtuple("UserPool", ["id", "name"])


class CognitoUserPools:

    def __init__(self, aws_region: str = "eu-west-1"):
        self.client = get_cognito_idp(aws_region)

    def list(self, max_results=10, next_token: str = None):
        response = None
        if next_token:
            response = self.client.list_user_pools(
                NextToken=next_token,
                MaxResults=max_results
            )
        else:
            response = self.client.list_user_pools(
                MaxResults=max_results
            )
        for obj in response["UserPools"]:
            yield UserPool(obj["Id"], obj["Name"])

    def describe(self, user_pool_id):
        return self.client.describe_user_pool(
            UserPoolId=user_pool_id
        )

    def delete(self, user_pool_id):
        return self.client.delete_user_pool(
            UserPoolId=user_pool_id
        )

    def create(self, full_name, pool_name):

        policies = {
            "PasswordPolicy": {
                "MinimumLength": 8,
                "RequireUppercase": True,
                "RequireLowercase": True,
                "RequireNumbers": True,
                # "RequireSymbols": True|False,
                "TemporaryPasswordValidityDays": 30
            }
        }

        lambdaConfig = {
            "PreSignUp": "string",
            "CustomMessage": "string",
            "PostConfirmation": "string",
            "PreAuthentication": "string",
            "PostAuthentication": "string",
            "DefineAuthChallenge": "string",
            "CreateAuthChallenge": "string",
            "VerifyAuthChallengeResponse": "string",
            "PreTokenGeneration": "string",
            "UserMigration": "string"
        }

        autoVerifiedAttributes = []
        aliasAttributes = ["email", "phone_number"]

        verificationMessageTemplate = {
            # "DefaultEmailOption": "CONFIRM_WITH_LINK"|"CONFIRM_WITH_CODE"
            "DefaultEmailOption": "CONFIRM_WITH_CODE",
            "EmailSubject": "Your verification code",
            "EmailMessage": "Your verification code is {####}. ",
            "EmailSubjectByLink": "Your verification link",
            "EmailMessageByLink": "Please click the link below to verify your email address. {##Verify Email##}",
            "SmsMessage": "Your username is {username} and temporary password is {####}.",
        }

        deviceConfiguration = {
            "ChallengeRequiredOnNewDevice": True | False,
            "DeviceOnlyRememberedOnUserPrompt": True | False
        }

        emailConfiguration = {
            # "SourceArn": "string",
            # "ReplyToEmailAddress": "string",
            "EmailSendingAccount": "COGNITO_DEFAULT",
            # "EmailSendingAccount": "COGNITO_DEFAULT"|"DEVELOPER",
            # "From": "string",
            # "ConfigurationSet": "string"
        }

        smsConfiguration = {
            "SnsCallerArn": "string",
            "ExternalId": "string"
        }

        userPoolTags = {
            "ignilife-customer": "yes",
            "ignilife-customer-name": full_name
        }

        adminCreateUserConfig = {
            "AllowAdminCreateUserOnly": True | False,
            "UnusedAccountValidityDays": 123,
            "InviteMessageTemplate": {
                "SMSMessage": "string",
                "EmailMessage": "string",
                "EmailSubject": "string"
            }
        }

        schema = []
        schema.append(SchemaAttributes["Email"])
        # schema.append(SchemaAttributes["PhoneNumber"])
        schema.append(SchemaAttributes["Custom_ObjectId"])
        schema.append(SchemaAttributes["Custom_OrgUnitId"])

        accountRecoverySetting = {
            "RecoveryMechanisms": [
                {
                    "Priority": 1,
                    "Name": "verified_email"
                },
                {
                    "Priority": 2,
                    "Name": "verified_phone_number"
                }
            ]
        }

        response = self.client.create_user_pool(
            PoolName=pool_name,
            Policies=policies,
            # LambdaConfig = lambdaConfig,
            AutoVerifiedAttributes=autoVerifiedAttributes,
            # AliasAttributes = aliasAttributes,
            UsernameAttributes=["email", "phone_number"],
            # SmsVerificationMessage="string",
            # EmailVerificationMessage="string",
            # EmailVerificationSubject="string",
            VerificationMessageTemplate=verificationMessageTemplate,
            # SmsAuthenticationMessage="string",
            MfaConfiguration="OFF",
            # DeviceConfiguration = deviceConfiguration,
            EmailConfiguration=emailConfiguration,
            # SmsConfiguration = smsConfiguration,
            UserPoolTags=userPoolTags,
            # AdminCreateUserConfig = adminCreateUserConfig,
            Schema=schema,
            UserPoolAddOns={
                "AdvancedSecurityMode": "OFF"
            },
            UsernameConfiguration={
                "CaseSensitive": False
            },
            AccountRecoverySetting=accountRecoverySetting
        )
        user_pool_id = response["UserPool"]["Id"]
        print(user_pool_id)
        return user_pool_id
