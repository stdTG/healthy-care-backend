import graphene

from app.user_roles.model import Roles


class RoleEnum(graphene.Enum):
    ADMIN = Roles.ADMIN
    SUPERVISOR = Roles.SUPERVISOR
    DOCTOR = Roles.DOCTOR
    NURSE = Roles.NURSE
    MEDICAL_ASSISTANT = Roles.MEDICAL_ASSISTANT
    OTHER = Roles.OTHER
    CONTENT_PUBLISHER = Roles.CONTENT_PUBLISHER
    BUSINESS_LEADER = Roles.BUSINESS_LEADER
    SUPERADMIN = Roles.SUPER_ADMIN
