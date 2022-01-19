import datetime
import re
from typing import Dict, Type

from mongoengine import Document

import app.users.common.models.db as dbm
import app.users.auth.web_model as wbm
from core.utils.random import Random
from core.utils.transaction import Transaction


def is_empty(txt: str):
    return txt is None or len(txt.strip()) == 0


def get_user_name(email: str, phone: str):
    """Default is [email]
    If [email] is empty then try [phone]
    If [phone] is empty too then None
    """
    username = email
    if is_empty(email):
        username = phone

    if is_empty(email) and is_empty(phone):
        return None

    return username


def is_email_exist(email: str, user_collection: Type[Document]):
    return user_collection.objects(email=email).first()


def is_phone_exist(phone: str, user_collection: Type[Document]):
    return user_collection.objects(phone=phone).first()


def set_verification_tokens(id_, email, phone, trx: Transaction = None) -> \
        Dict[str, dbm.UserVerification]:

    print("[VERIFICATION-TOKENS] Start generation")

    def rollback(obj: dbm.UserVerification):
        print("[VERIFICATION-TOKENS-ROLLBACK] Verification")
        obj.delete()

    def init(type_, username, tokens_expire, trx):
        if not username:
            return

        print(f"[VERIFICATION-TOKENS] Generating for: {username}")
        data = Random.get_verification_secrets()
        obj = dbm.UserVerification()
        obj.user_id = id_
        obj.type_ = type_
        obj.username = username
        obj.token = data.token
        obj.tokenExpires = tokens_expire
        obj.code = data.code
        obj.attempts = 0
        obj.status = wbm.CredentialStatusEnum.REQUIRE_VERIFICATION
        obj.save()

        if trx:
            trx.push(rollback, obj)
        return obj

    expiration = datetime.datetime.utcnow() + datetime.timedelta(minutes=30)

    res = {
        "email": init("email", email, expiration, trx),
        "phone": init("phone", phone, expiration, trx)
    }

    print("[VERIFICATION-TOKENS] Done")
    return res


def create_regexp(str_: str):
    str_ = str_.lower()
    return re.compile(f".*{str_}.*", re.IGNORECASE)
