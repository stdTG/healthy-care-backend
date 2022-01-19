from datetime import datetime
from typing import Any, List, Optional

from web.core.results import CamelModel


class SendbirdUserOut(CamelModel):
    app_id: str
    access_token: str
    session_token: str
    session_token_expired: datetime


class SendbirdSettingsOut(CamelModel):
    app_id: str
    token: Optional[str]


class SendbirdTokenOut(CamelModel):
    token: str
    created_at: datetime


class SendbirdTokensOut(CamelModel):
    tokens: List[SendbirdTokenOut]


class SendbirdApiResponse(CamelModel):
    data: Any
