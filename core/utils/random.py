import hashlib
import random
from collections import namedtuple
from uuid import UUID, uuid1

RandomTuple = namedtuple("RandomTuple", ["uuid", "short_code"])
UserVerificationSecrets = namedtuple("UserVerificationSecrets", ["code", "token"])


class Random:

    @classmethod
    def get(cls) -> RandomTuple:
        uuid_value: UUID = uuid1()
        hasher = hashlib.sha1(uuid_value.bytes)
        short_code = hasher.hexdigest()[:9]
        return RandomTuple(uuid_value, short_code)

    @classmethod
    def get_verification_secrets(cls) -> UserVerificationSecrets:
        code = str(random.randrange(1001, 9999, 1))
        uuid_value: UUID = uuid1()
        token = hashlib.sha1(uuid_value.bytes).hexdigest()
        return UserVerificationSecrets(code, token)

    @classmethod
    def password(cls) -> str:
        uuid_value: UUID = uuid1()
        hasher = hashlib.sha1(uuid_value.bytes)
        return hasher.hexdigest()[:8] + "X"
