import graphene


class SexEnum(graphene.Enum):
    UNDEFINED = 'n/a'
    MALE = 'male'
    FEMALE = 'female'
    OTHER = 'other'
