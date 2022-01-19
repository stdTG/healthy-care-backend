from typing import Any, Optional

from pydantic import Field

from web.core.results import CamelModel


class MessageBody(CamelModel):
    version: str = Field(example="1.0.0")
    user_response: Any


class Message(CamelModel):
    version: str = Field(example="1.0.0")
    type: str = Field(example="Message")
    body: MessageBody


class Message_Simple(Message):
    type: str = Field(example="Message_Simple")


class Message_Question(Message):
    type: str = Field(example="Message_Question")
    care_plan_assignment_id: str = Field(example="5f8d0ed1ae0622e62729eb9d")
    body: MessageBody
    callback_token: Optional[str] = Field(example="R4ga3A1aksdfjas3493493jja351456#4a3Saaa34ss")
