import graphene


class Login(graphene.Interface):
    email = graphene.String(required=True)
    password = graphene.String(required=True)


class UserByEmail(graphene.ObjectType):
    email = graphene.String(required=True)


class UserByPhone(graphene.ObjectType):
    phone = graphene.String(required=True)


class User:
    id_ = graphene.String(required=True)
    firstName = graphene.String(required=True)
    lastName = graphene.String(required=True)

    # contacts
    byPhone = graphene.Field(UserByPhone)
    byEmail = graphene.Field(UserByEmail)

    # demographics
    language = graphene.String()
