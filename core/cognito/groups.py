from core.config import get_app_config
from core.utils.aws import get_cognito_idp


class CognitoGroups:

    def __init__(self, aws_region: str = "eu-west-1"):
        # cfg = get_app_config()
        self.client = get_cognito_idp(aws_region)

    def admin_list_groups_for_user(self, username: str, user_pool_id: str, limit: int = None,
                                   next_token: str = None):
        args = {"Username": username, "UserPoolId": user_pool_id}
        if limit:
            args["Limit"] = limit
        if next_token:
            args["NextToken"] = next_token

        data = self.client.admin_list_groups_for_user(**args)

        next_token = None
        if hasattr(data, "NextToken"):
            next_token = data["NextToken"]

        return {
            "groups": [grp["GroupName"] for grp in data["Groups"]],
            "next_token": next_token
        }

    def remove_user_from_group(self):
        return self.client.admin_remove_user_from_group()

    def create(self, user_pool_id, groupname):
        return self.client.create_group(
            UserPoolId=user_pool_id,
            GroupName=groupname,
        )

    def delete_group(self):
        return self.client.delete_group()

    def get_group(self):
        return self.client.get_group()

    def list_groups(self):
        return self.client.list_groups()

    def list_users_in_group(self):
        return self.client.list_users_in_group()

    def update_group(self):
        return self.client.update_group()
