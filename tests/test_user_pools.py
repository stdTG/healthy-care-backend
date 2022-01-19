from core.cognito import CognitoUserPools


def test_list(aws_ctx):
    user_pools = CognitoUserPools(aws_ctx.region)
    data_list = user_pools.list()
    for upool in data_list:
        print(f"{upool.id} | {upool.name}")
