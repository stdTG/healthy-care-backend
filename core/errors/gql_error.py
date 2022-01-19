import graphene

from core.utils.str_enum import StrEnum


class ErrorEnum(StrEnum):
    NOT_AUTHENTICATED = "NOT_AUTHENTICATED"
    TITLE_ALREADY_TAKEN = "TITLE_ALREADY_TAKEN"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    GRAPHQL_VALIDATION_FAILED = "GRAPHQL_VALIDATION_FAILED"
    SERVER_ERROR = "SERVER_ERROR"
    NOT_FOUND = "NOT_FOUND"
    NOT_AVAILABLE = "NOT_AVAILABLE"


class ErrorInterface(graphene.Interface):
    # Constant error code
    code = graphene.String(required=True)
    # Source of the error from the model path
    message = graphene.String()


class Error(graphene.ObjectType):
    class Meta:
        interfaces = [ErrorInterface, ]


class NotAuthenticatedError(graphene.ObjectType):
    code = graphene.String(required=True, default_value=ErrorEnum.NOT_AUTHENTICATED)

    class Meta:
        interfaces = [ErrorInterface, ]


class TitleAlreadyTakenError(graphene.ObjectType):
    """When field already in database and it must be unique."""
    code = graphene.String(required=True, default_value=ErrorEnum.TITLE_ALREADY_TAKEN)
    path = graphene.String()

    class Meta:
        interfaces = [ErrorInterface, ]


class ServerError(graphene.ObjectType):
    """When an unknown error occurs on the server."""
    code = graphene.String(required=True, default_value=ErrorEnum.SERVER_ERROR)
    message = graphene.String(required=True, default_value="Internal Server Error")

    class Meta:
        interfaces = [ErrorInterface, ]


class ValidationError(graphene.ObjectType):
    """Input data validation error."""
    code = graphene.String(required=True, default_value=ErrorEnum.GRAPHQL_VALIDATION_FAILED)
    # Field value which occurs the validation error
    path = graphene.String()
    # Value of field
    value = graphene.String()

    class Meta:
        interfaces = [ErrorInterface, ]


class NotFoundError(graphene.ObjectType):
    """The object is not found in the database."""
    code = graphene.String(required=True, default_value=ErrorEnum.NOT_FOUND)

    class Meta:
        interfaces = [ErrorInterface, ]


class NotAvailableError(graphene.ObjectType):
    """The object is not found in the database."""
    code = graphene.String(required=True, default_value=ErrorEnum.NOT_AVAILABLE)
    message = graphene.String(default_value="The time is already taken")

    class Meta:
        interfaces = [ErrorInterface, ]
