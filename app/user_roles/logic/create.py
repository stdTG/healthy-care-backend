from core.cognito import CognitoGroups
from ..model import Roles


class Create:

    def __init__(self):
        self.c_groups = CognitoGroups()

    def default_roles(self, user_pool_id: str, make_super_admin: bool = False):
        self.c_groups.create(user_pool_id, Roles.ADMIN)
        self.c_groups.create(user_pool_id, Roles.SUPERVISOR)
        self.c_groups.create(user_pool_id, Roles.DOCTOR)
        self.c_groups.create(user_pool_id, Roles.NURSE)
        self.c_groups.create(user_pool_id, Roles.MEDICAL_ASSISTANT)
        self.c_groups.create(user_pool_id, Roles.OTHER)
        self.c_groups.create(user_pool_id, Roles.CONTENT_PUBLISHER)
        self.c_groups.create(user_pool_id, Roles.BUSINESS_LEADER)
        self.c_groups.create(user_pool_id, Roles.PATIENT)

        if make_super_admin:
            self.c_groups.create(user_pool_id, Roles.SUPER_ADMIN)
