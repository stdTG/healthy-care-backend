from pydantic import Field

from .base_web import Message, MessageBody


# basic_input / text
class MessageBody_BasicInput_Text_Prompt(MessageBody):
    prompt: str = Field(example="Please, enter some value")


class Message_BasicInput_Text_Prompt(Message):
    body: MessageBody_BasicInput_Text_Prompt


class MessageBody_BasicInput_Text_Response(MessageBody):
    userResponse: str = Field(example="User response")


class Message_BasicInput_Text_Response(Message):
    body: MessageBody_BasicInput_Text_Response


# basic_input / with_placeholder
class MessageBody_BasicInput_WithPlaceholder_Prompt(MessageBody):
    prompt: str = Field(example="Please, enter some value")


class Message_BasicInput_WithPlaceholder_Prompt(Message):
    body: MessageBody_BasicInput_WithPlaceholder_Prompt


class MessageBody_BasicInput_WithPlaceholder_Response(MessageBody):
    userResponse: str = Field(example="User response")


class Message_BasicInput_WithPlaceholder_Response(Message):
    body: MessageBody_BasicInput_WithPlaceholder_Response


# basic_input / with_unit
class MessageBody_BasicInput_WithUnit_Prompt(MessageBody):
    prompt: str = Field(example="Please, enter some value")


class Message_BasicInput_WithUnit_Prompt(Message):
    body: MessageBody_BasicInput_WithUnit_Prompt


class MessageBody_BasicInput_WithUnit_Response(MessageBody):
    userResponse: str = Field(example="User response")


class Message_BasicInput_WithUnit_Response(Message):
    body: MessageBody_BasicInput_WithUnit_Response


# basic_input / dropdown
class MessageBody_BasicInput_Dropdown_Prompt(MessageBody):
    prompt: str = Field(example="Please, enter some value")


class Message_BasicInput_Dropdown_Prompt(Message):
    body: MessageBody_BasicInput_Dropdown_Prompt


class MessageBody_BasicInput_Dropdown_Response(MessageBody):
    userResponse: str = Field(example="User response")


class Message_BasicInput_Dropdown_Response(Message):
    body: MessageBody_BasicInput_Dropdown_Response


# basic_input / radiobuttons
class MessageBody_BasicInput_Radiobuttons_Prompt(MessageBody):
    prompt: str = Field(example="Please, enter some value")


class Message_BasicInput_Radiobuttons_Prompt(Message):
    body: MessageBody_BasicInput_Radiobuttons_Prompt


class MessageBody_BasicInput_Radiobuttons_Response(MessageBody):
    userResponse: str = Field(example="User response")


class Message_BasicInput_Radiobuttons_Response(Message):
    body: MessageBody_BasicInput_Radiobuttons_Response


# basic_input / checkboxes
class MessageBody_BasicInput_Checkboxes_Prompt(MessageBody):
    prompt: str = Field(example="Please, enter some value")


class Message_BasicInput_Checkboxes_Prompt(Message):
    body: MessageBody_BasicInput_Checkboxes_Prompt


class MessageBody_BasicInput_Checkboxes_Response(MessageBody):
    userResponse: str = Field(example="User response")


class Message_BasicInput_Checkboxes_Response(Message):
    body: MessageBody_BasicInput_Checkboxes_Response


# basic_input / chips
class MessageBody_BasicInput_Chips_Prompt(MessageBody):
    prompt: str = Field(example="Please, enter some value")


class Message_BasicInput_Chips_Prompt(Message):
    body: MessageBody_BasicInput_Chips_Prompt


class MessageBody_BasicInput_Chips_Response(MessageBody):
    userResponse: str = Field(example="User response")


class Message_BasicInput_Chips_Response(Message):
    body: MessageBody_BasicInput_Chips_Response


# basic_input / slider
class MessageBody_BasicInput_Slider_Prompt(MessageBody):
    prompt: str = Field(example="Please, enter some value")


class Message_BasicInput_Slider_Prompt(Message):
    body: MessageBody_BasicInput_Slider_Prompt


class MessageBody_BasicInput_Slider_Response(MessageBody):
    userResponse: str = Field(example="User response")


class Message_BasicInput_Slider_Response(Message):
    body: MessageBody_BasicInput_Slider_Response


# basic_input / switch
class MessageBody_BasicInput_Switch_Prompt(MessageBody):
    prompt: str = Field(example="Please, enter some value")


class Message_BasicInput_Switch_Prompt(Message):
    body: MessageBody_BasicInput_Switch_Prompt


class MessageBody_BasicInput_Switch_Response(MessageBody):
    userResponse: str = Field(example="User response")


class Message_BasicInput_Switch_Response(Message):
    body: MessageBody_BasicInput_Switch_Response


# basic_input / appointment
class MessageBody_BasicInput_Appointment_Prompt(MessageBody):
    prompt: str = Field(example="Please, enter some value")


class Message_BasicInput_Appointment_Prompt(Message):
    body: MessageBody_BasicInput_Appointment_Prompt


class MessageBody_BasicInput_Appointment_Response(MessageBody):
    userResponse: str = Field(example="User response")


class Message_BasicInput_Appointment_Response(Message):
    body: MessageBody_BasicInput_Appointment_Response


# basic_input / prescription_reminder
class MessageBody_BasicInput_PrescriptionReminder_Prompt(MessageBody):
    prompt: str = Field(example="Please, enter some value")


class Message_BasicInput_PrescriptionReminder_Prompt(Message):
    body: MessageBody_BasicInput_PrescriptionReminder_Prompt


class MessageBody_BasicInput_PrescriptionReminder_Response(MessageBody):
    userResponse: str = Field(example="User response")


class Message_BasicInput_PrescriptionReminder_Response(Message):
    body: MessageBody_BasicInput_PrescriptionReminder_Response
