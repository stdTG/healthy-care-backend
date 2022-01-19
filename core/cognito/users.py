from collections import namedtuple
from typing import List

from core.config import get_app_config
from core.utils.aws import get_cognito_idp
from core.utils.transaction import Transaction

# AWS COGNITO Documentation
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cognito-idp.html


CognitoUser = namedtuple("CognitoUser",
                         ["user_pool_id", "username", "email", "phone_number", "objectid",
                          "orgunitid", "sub", "enabled", "status"])
CognitoNewUser = namedtuple("CognitoNewUser",
                            ["user_pool_id", "username", "email", "phone_number", "temp_password",
                             "objectid", "orgunitid"])


class CognitoUsers:

    def __init__(self, aws_region: str = "eu-west-1"):
        self.client = get_cognito_idp(aws_region)

    def sign_up_email(self, client_id, email, password):
        return self.client.sign_up(
            ClientId=client_id,
            Username=email,
            Password=password
        )

    def sign_up_phone(self, client_id, phone_number, password):
        return self.client.sign_up(
            ClientId=client_id,
            Username=phone_number,
            Password=password
        )

    def sign_up(self, client_id, username, email, phone_number, password):
        return self.client.sign_up(
            ClientId=client_id,
            Username=username,
            Password=password,
            UserAttributes=[
                {
                    "Name": "email",
                    "Value": email
                },
                {
                    "Name": "phone_number",
                    "Value": phone_number
                },
            ],
        )

    def confirm_sign_up_email(self, client_id, email, code):
        return self.client.confirm_sign_up(
            ClientId=client_id,
            Username=email,
            ConfirmationCode=code
        )

    def confirm_sign_up_phone(self, client_id, phone, code):
        return self.client.confirm_sign_up(
            ClientId=client_id,
            Username=phone,
            ConfirmationCode=code
        )

    def __get_attr(self, cognito_attributes, attribute_name):
        for attr in cognito_attributes:
            if attr["Name"] == attribute_name:
                return attr["Value"]
        return None

    def list_users(self, user_pool_id, attributes_to_get=None, limit=None, pagination_token=None,
                   filter_=None) -> List[CognitoUser]:

        args = {}
        args["UserPoolId"] = user_pool_id

        if attributes_to_get:
            args["AttributesToGet"] = attributes_to_get
        if limit:
            args["Limit"] = limit
        if pagination_token:
            args["PaginationToken"] = pagination_token
        if filter_:
            args["Filter"] = filter_
        data = self.client.list_users(**args)["Users"]

        new_pagination_token = None
        if hasattr(data, "PaginationToken"):
            new_pagination_token = data.PaginationToken

        def __enumerate(cgt_users):
            for data in cgt_users:
                attributes = data["Attributes"]

                yield CognitoUser(
                    user_pool_id=user_pool_id,
                    username=data["Username"],
                    sub=self.__get_attr(attributes, "sub"),
                    email=self.__get_attr(attributes, "email"),
                    phone_number=self.__get_attr(attributes, "phone_number"),
                    objectid=self.__get_attr(attributes, "custom:objectid"),
                    orgunitid=self.__get_attr(attributes, "custom:orgunitid"),
                    enabled=data["Enabled"],
                    status=data["UserStatus"],
                )

        return __enumerate(data)

    def get_user(self, user_pool_id, username):
        data = self.client.admin_get_user(
            UserPoolId=user_pool_id,
            Username=username
        )
        attributes = data["UserAttributes"]

        return CognitoUser(
            user_pool_id=user_pool_id,
            username=data["Username"],
            email=self.__get_attr(attributes, "email"),
            phone_number=self.__get_attr(attributes, "phone_number"),
            objectid=self.__get_attr(attributes, "custom:objectid"),
            orgunitid=self.__get_attr(attributes, "custom:orgunitid"),
            sub=data["Username"],
            enabled=data["Enabled"],
            status=data["UserStatus"],
        )

    def create(self, user: CognitoNewUser, ctx: Transaction = None):
        return self.client.admin_create_user(
            UserPoolId=user.user_pool_id,
            Username=user.username,
            # TemporaryPassword=user.temp_password,
            # MessageAction="SUPPRESS",
            MessageAction="SUPPRESS",
            UserAttributes=[
                {
                    "Name": "email",
                    "Value": user.email
                },
                {
                    "Name": "phone_number",
                    "Value": user.phone_number,
                },
                {
                    "Name": "custom:objectid",
                    "Value": user.objectid
                },
                {
                    "Name": "custom:orgunitid",
                    "Value": user.orgunitid
                },
            ],
        )

    def delete(self, user_pool_id, username):
        return self.client.admin_delete_user(
            UserPoolId=user_pool_id,
            Username=username
        )

    def set_password(self, user_pool_id, username, password, permanent=True):
        return self.client.admin_set_user_password(
            UserPoolId=user_pool_id,
            Username=username,
            Password=password,
            Permanent=permanent,
        )

    def add_to_group(self, user_pool_id, username, groupname):
        return self.client.admin_add_user_to_group(
            UserPoolId=user_pool_id,
            Username=username,
            GroupName=groupname,
        )

    def delete_from_group(self, user_pool_id, username, group_name):
        return self.client.admin_remove_user_from_group(
            UserPoolId=user_pool_id,
            Username=username,
            GroupName=group_name,
        )

    def set_user_attribute(self, user_pool_id, username, attribute_name, attribute_value):
        return self.client.admin_update_user_attributes(
            UserPoolId=user_pool_id,
            Username=username,
            UserAttributes=[
                {
                    "Name": attribute_name,
                    "Value": attribute_value,
                }
            ],
        )

    def set_orgunit(self, user_pool_id, username, org_unit_id):
        return self.client.admin_update_user_attributes(
            UserPoolId=user_pool_id,
            Username=username,
            UserAttributes=[
                {
                    "Name": "custom:orgunitid",
                    "Value": org_unit_id,
                }
            ],
        )
