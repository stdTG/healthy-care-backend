from typing import List, Optional

from pydantic import BaseModel, Field

from core.utils.str_enum import StrEnum
from app.feed.models.base_web import Message, MessageBody, Message_Question
from web.core.results import CamelModel


class MessageTypePrompt(StrEnum):
    question_text = "Message_Question_Text_Prompt"
    number_simple = "Message_Question_NumberSimple_Prompt"
    number_scale = "Message_Question_NumberScale_Prompt"
    address = "Message_Question_Address_Prompt"
    date = "Message_Question_Date_Prompt"
    file_upload = "Message_Question_FileUpload_Prompt"
    labels = "Message_Question_Labels_Prompt"
    multiple_choice = "Message_Question_MultipleChoice_Prompt"
    phone = "Message_Question_Phone_Prompt"
    picture_choice = "Message_Question_PictureChoice_Prompt"
    rating = "Message_Question_Rating_Prompt"
    time = "Message_Question_Time_Prompt"
    yes_no = "Message_Question_YesNo_Prompt"
    action_card = "Message_Question_ActionCard_Prompt"
    text = "Message_Text_Prompt"


class MessageTypeResponse(StrEnum):
    text = "Message_Text_Response"
    number_simple = "Message_Question_NumberSimple_Response"
    number_scale = "Message_Question_NumberScale_Response"
    address = "Message_Question_Address_Response"
    date = "Message_Question_Date_Response"
    file_upload = "Message_Question_FileUpload_Response"
    labels = "Message_Question_Labels_Response"
    multiple_choice = "Message_Question_MultipleChoice_Response"
    phone = "Message_Question_Phone_Response"
    picture_choice = "Message_Question_PictureChoice_Response"
    rating = "Message_Question_Rating_Response"
    time = "Message_Question_Time_Response"
    yes_no = "Message_Question_YesNo_Response"
    action_card = "Message_Question_ActionCard_Response"


# question / text
class MessageBody_Question_Text_Prompt(MessageBody):
    prompt: str = Field(example="Please, enter some value")


class Message_Question_Text_Prompt(Message_Question):
    type: str = Field(example=MessageTypePrompt.text)
    body: MessageBody_Question_Text_Prompt


class MessageBody_Question_Text_Response(MessageBody):
    user_response: str = Field(example="User response")


class Message_Question_Text_Response(Message_Question):
    type: str = Field(example=MessageTypeResponse.text)
    body: MessageBody_Question_Text_Response


# question / number_simple
class MessageBody_Question_NumberSimple_Prompt(MessageBody):
    prompt: str = Field(example="Please, enter some value")
    min: int = Field(example="0")
    max: int = Field(example="5")
    prefix: str = Field(example="Kilo-kg")


class Message_Question_NumberSimple_Prompt(Message_Question):
    type: str = Field(example=MessageTypePrompt.number_simple,
                      default=MessageTypePrompt.number_simple)
    body: MessageBody_Question_NumberSimple_Prompt


class MessageBody_Question_NumberSimple_Response(MessageBody):
    user_response: str = Field(example="User response")


class Message_Question_NumberSimple_Response(Message_Question):
    type: str = Field(example=MessageTypeResponse.number_simple)
    body: MessageBody_Question_NumberSimple_Response


class Score(CamelModel):
    start: int
    end: int
    score: int


# question / number_scale
class MessageBody_Question_NumberScale_Prompt(MessageBody):
    prompt: str = Field(example="Please, enter some value")
    start_scale: int = Field(example=5)
    end_scale: int = Field(example=5)
    left_label: int = Field(example=1)
    center_label: int = Field(example=12)
    right_label: int = Field(example=24)
    scores: List[Score]


class Message_Question_NumberScale_Prompt(Message_Question):
    type: str = Field(example=MessageTypePrompt.number_scale)
    body: MessageBody_Question_NumberScale_Prompt


class MessageBody_Question_NumberScale_Response(MessageBody):
    user_response: str = Field(example="User response")


class Message_Question_NumberScale_Response(Message_Question):
    type: str = Field(example=MessageTypeResponse.number_scale)
    body: MessageBody_Question_NumberScale_Response


# question / address
class MessageBody_Question_Address_Prompt(MessageBody):
    prompt: str = Field(example="Please, enter some value")


class Message_Question_Address_Prompt(Message_Question):
    type: str = Field(example=MessageTypePrompt.address)
    body: MessageBody_Question_Address_Prompt


class MessageBody_Question_Address_Response(MessageBody):
    user_response: str = Field(example="User response")


class Message_Question_Address_Response(Message_Question):
    type: str = Field(example=MessageTypeResponse.address)
    body: MessageBody_Question_Address_Response


# question / date
class MessageBody_Question_Date_Prompt(MessageBody):
    prompt: str = Field(example="Please, enter some value")
    format: str = Field(example="MMDDYYYY")


class Message_Question_Date_Prompt(Message_Question):
    type: str = Field(example=MessageTypePrompt.date)
    body: MessageBody_Question_Date_Prompt


class MessageBody_Question_Date_Response(MessageBody):
    user_response: str = Field(example="User response")


class Message_Question_Date_Response(Message_Question):
    type: str = Field(example=MessageTypeResponse.date)
    body: MessageBody_Question_Date_Response


# question / file_upload
class MessageBody_Question_FileUpload_Prompt(MessageBody):
    prompt: str = Field(example="Please, enter some value")


class Message_Question_FileUpload_Prompt(Message_Question):
    type: str = Field(example=MessageTypePrompt.file_upload)
    body: MessageBody_Question_FileUpload_Prompt


class MessageBody_Question_FileUpload_Response(MessageBody):
    user_response: str = Field(example="User response")


class Message_Question_FileUpload_Response(Message_Question):
    type: str = Field(example=MessageTypeResponse.file_upload)
    body: MessageBody_Question_FileUpload_Response


# question / labels
class MessageBody_Question_Labels_Prompt(MessageBody):
    prompt: str = Field(example="Please, enter some value")


class Message_Question_Labels_Prompt(Message_Question):
    type: str = Field(example=MessageTypePrompt.labels)
    body: MessageBody_Question_Labels_Prompt


class MessageBody_Question_Labels_Response(MessageBody):
    user_response: str = Field(example="User response")


class Message_Question_Labels_Response(Message_Question):
    type: str = Field(example=MessageTypeResponse.labels)
    body: MessageBody_Question_Labels_Response


# question / multiple_choice

class Choice(BaseModel):
    text: str = Field(example="a")
    number: int = Field(example=1)


class MessageBody_Question_MultipleChoice_Prompt(MessageBody):
    prompt: str = Field(example="Please, enter some value")
    answers: List[Choice]
    multiselect: bool = Field(example=True)


class Message_Question_MultipleChoice_Prompt(Message_Question):
    type: str = Field(example=MessageTypePrompt.multiple_choice)
    body: MessageBody_Question_MultipleChoice_Prompt


class MessageBody_Question_MultipleChoice_Response(MessageBody):
    user_response: int = Field(example="User response")


class Message_Question_MultipleChoice_Response(Message_Question):
    type: str = Field(example=MessageTypeResponse.multiple_choice)
    body: MessageBody_Question_MultipleChoice_Response


# question / phone
class MessageBody_Question_Phone_Prompt(MessageBody):
    prompt: str = Field(example="Please, enter some value")
    code: str = Field(example="+7")


class Message_Question_Phone_Prompt(Message_Question):
    type: str = Field(example=MessageTypePrompt.phone)
    body: MessageBody_Question_Phone_Prompt


class MessageBody_Question_Phone_Response(MessageBody):
    user_response: str = Field(example="User response")


class Message_Question_Phone_Response(Message_Question):
    type: str = Field(example=MessageTypeResponse.phone)
    body: MessageBody_Question_Phone_Response


# question / picture_choice
class MessageBody_Question_PictureChoice_Prompt(MessageBody):
    prompt: str = Field(example="Please, enter some value")


class Message_Question_PictureChoice_Prompt(Message_Question):
    type: str = Field(example=MessageTypePrompt.picture_choice)
    body: MessageBody_Question_PictureChoice_Prompt


class MessageBody_Question_PictureChoice_Response(MessageBody):
    user_response: str = Field(example="User response")


class Message_Question_PictureChoice_Response(Message_Question):
    type: str = Field(example=MessageTypeResponse.picture_choice)
    body: MessageBody_Question_PictureChoice_Response


# question / rating
class MessageBody_Question_Rating_Prompt(MessageBody):
    prompt: str = Field(example="Please, enter some value")
    rating_shape: str = Field(example="stars")
    steps: int = Field(example="5")


class Message_Question_Rating_Prompt(Message_Question):
    type: str = Field(example=MessageTypePrompt.rating)
    body: MessageBody_Question_Rating_Prompt


class MessageBody_Question_Rating_Response(MessageBody):
    user_response: str = Field(example="User response")


class Message_Question_Rating_Response(Message_Question):
    type: str = Field(example=MessageTypeResponse.rating)
    body: MessageBody_Question_Rating_Response


# question / time
class MessageBody_Question_Time_Prompt(MessageBody):
    prompt: str = Field(example="Please, enter some value")


class Message_Question_Time_Prompt(Message_Question):
    type: str = Field(example=MessageTypePrompt.time)
    body: MessageBody_Question_Time_Prompt


class MessageBody_Question_Time_Response(MessageBody):
    user_response: str = Field(example="User response")


class Message_Question_Time_Response(Message_Question):
    type: str = Field(example=MessageTypeResponse.time)
    body: MessageBody_Question_Time_Response


# question / yes_no
class MessageBody_Question_YesNo_Prompt(MessageBody):
    prompt: str = Field(example="Please, enter some value")


class Message_Question_YesNo_Prompt(Message_Question):
    yes_field: str = Field(example="Agree")
    no_field: str = Field(example="Disagree")
    type: str = Field(example=MessageTypePrompt.yes_no)
    body: MessageBody_Question_YesNo_Prompt


class MessageBody_Question_YesNo_Response(MessageBody):
    user_response: str = Field(example="User response")


class Message_Question_YesNo_Response(Message_Question):
    type: str = Field(example=MessageTypeResponse.yes_no)
    body: MessageBody_Question_YesNo_Response


class MessageBody_Action_Card_Prompt(MessageBody):
    category: str = Field(example="Yoga")
    description: str = Field(example="long description")
    tips: str = Field(example="how to do")
    url: str = Field(example="youtube link or smth")


class Message_Action_Card_Prompt(Message):
    type: str = Field(example=MessageTypePrompt.action_card)
    body: MessageBody_Action_Card_Prompt
    care_plan_assignment_id: str = Field(example="5f8d0ed1ae0622e62729eb9d")
    callback_token: Optional[str] = Field(example="R4ga3A1aksdfjas3493493jja351456#4a3Saaa34ss")


class MessageBody_Text_Prompt(MessageBody):
    text: str = Field(example="Yoga")


class Message_Text_Prompt(Message):
    type: str = Field(example=MessageTypePrompt.text)
    body: MessageBody_Text_Prompt
