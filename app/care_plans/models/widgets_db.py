from mongoengine import ObjectIdField, URLField, EmbeddedDocument, EmbeddedDocumentListField
from mongoengine.fields import BooleanField, DecimalField, IntField, ListField, StringField

from app.care_plans.models.care_plan_db import DbWidget, Question

QUESTION_CELERY_TASKS = {}

# question / text
QUESTION_CELERY_TASKS["Question_Text"] = {
    "prompt": "care_plans.question.text_prompt",
    "response": "care_plans.question.text_response"
}


class Question_Text(Question):
    addToNotes = BooleanField()
    dataTypeId = ObjectIdField()


# question / number_simple
QUESTION_CELERY_TASKS["Question_NumberSimple"] = {
    "prompt": "care_plans.question.number_simple_prompt",
    "response": "care_plans.question.number_simple_response"
}


class Question_NumberSimple(Question):
    min = DecimalField(required=True, )
    max = DecimalField(required=True)
    prefix_id = ObjectIdField()


# question / number_scale
QUESTION_CELERY_TASKS["Question_NumberScale"] = {
    "prompt": "care_plans.question.number_scale_prompt",
    "response": "care_plans.question.number_scale_response"
}


class Score(EmbeddedDocument):
    start_value = IntField()
    end_value = IntField()
    result_score = IntField()


class Question_NumberScale(Question):
    start_scale = IntField()
    end_scale = IntField()
    left_label = IntField()
    center_label = IntField()
    right_label = IntField()
    scores = ListField(Score)


# question / address
QUESTION_CELERY_TASKS["Question_Address"] = {
    "prompt": "care_plans.question.address_prompt",
    "response": "care_plans.question.address_response"
}


class Question_Address(Question):
    pass


# question / date
QUESTION_CELERY_TASKS["Question_Date"] = {
    "prompt": "care_plans.question.date_prompt",
    "response": "care_plans.question.date_response"
}


class Question_Date(Question):
    format = StringField()


# question / file_upload
QUESTION_CELERY_TASKS["Question_FileUpload"] = {
    "prompt": "care_plans.question.file_upload_prompt",
    "response": "care_plans.question.file_upload_response"
}


class Question_FileUpload(Question):
    pass


# question / labels
QUESTION_CELERY_TASKS["Question_Labels"] = {
    "prompt": "care_plans.question.labels_prompt",
    "response": "care_plans.question.labels_response"
}


class Question_Labels(Question):
    pass


# question / multiple_choice
QUESTION_CELERY_TASKS["Question_MultipleChoice"] = {
    "prompt": "care_plans.question.multiple_choice_prompt",
    "response": "care_plans.question.multiple_choice_response"
}


class Choice(EmbeddedDocument):
    text = StringField()
    score = StringField()
    next_widget = StringField()
    number = IntField()


class Question_MultipleChoice(Question):
    is_multiselect = BooleanField(default=False)
    answers = EmbeddedDocumentListField(Choice)


# question / phone
QUESTION_CELERY_TASKS["Question_Phone"] = {
    "prompt": "care_plans.question.phone_prompt",
    "response": "care_plans.question.phone_response"
}


class Question_Phone(Question):
    countryCode = StringField()


# question / picture_choice
QUESTION_CELERY_TASKS["Question_PictureChoice"] = {
    "prompt": "care_plans.question.picture_choice_prompt",
    "response": "care_plans.question.picture_choice_response"
}


class Question_PictureChoice(Question):
    pass


# question / rating
QUESTION_CELERY_TASKS["Question_Rating"] = {
    "prompt": "care_plans.question.rating_prompt",
    "response": "care_plans.question.rating_response"
}


class Question_Rating(Question):
    steps = IntField()
    ratingShape = StringField()


# question / time
QUESTION_CELERY_TASKS["Question_Time"] = {
    "prompt": "care_plans.question.time_prompt",
    "response": "care_plans.question.time_response"
}


class Question_Time(Question):
    pass


# question / yes_no
QUESTION_CELERY_TASKS["Question_YesNo"] = {
    "prompt": "care_plans.question.yes_no_prompt",
    "response": "care_plans.question.yes_no_response"
}


class Question_YesNo(Question):
    dataTypeId = ObjectIdField()
    scoreYes = IntField()
    scoreNo = IntField()


QUESTION_CELERY_TASKS["Action_Card"] = {
    "prompt": "care_plans.question.action_card",
    "response": ""
}


class ActionCard(DbWidget):
    categoryId = ObjectIdField()
    description = StringField()
    tips = StringField()
    url = URLField()
    icon = StringField(required=True, default="default")


QUESTION_CELERY_TASKS["Text"] = {
    "prompt": "care_plans.question.text",
    "response": ""
}


class Text(DbWidget):
    icon = StringField(required=True, default="default")
    text = StringField(required=True)


QUESTION_CELERY_TASKS["Message"] = {
    "prompt": "care_plans.question.calculator",
    "response": ""
}


class Calculator(DbWidget):
    formula = StringField()
    resultVarName = StringField()
