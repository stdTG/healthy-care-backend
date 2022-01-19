from pycognito import Cognito, UserObj


async def sign_in_jwt(
        user_pool_id: str,
        client_id: str,
        username: str,
        password: str
):
    client = Cognito(user_pool_id, client_id, username=username)
    client.authenticate(password=password)
    _: UserObj = client.get_user()
    return {
        "id_token": client.id_token,
        "access_token": client.access_token,
        "refresh_token": client.refresh_token,
        "username": client.username,
        "base_attributes": client.base_attributes,
        "attr": client.custom_attributes,
        "user": None
    }
