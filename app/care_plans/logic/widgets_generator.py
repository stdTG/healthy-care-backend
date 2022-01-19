import json
import random
from enum import IntEnum
from typing import Dict, List

from app.care_plans.models.care_plan_db import DbWidget
from app.care_plans.models.widgets_db import \
    (Choice, Question_NumberScale, Score, Text, Question_MultipleChoice, Question_NumberSimple)


class VertexTypes(IntEnum):
    default = 0
    text = 1
    scale = 2
    library_content = 3
    map = 4
    data = 5
    questionnaire = 6
    text_input = 7
    choices = 8
    message = 9
    appointment = 10
    question = 11
    action = 12
    container = 13
    multiple_choice = 14
    number_simple = 15


def parse_json(ui_json):
    edges = {}
    vertices = {}

    for el in ui_json:
        if el.get("vertex"):
            vertices[el.get("id")] = el
        else:
            print(el.get("source"))
            edges[el.get("source")] = el

    return edges, vertices


def process_text(widget_json: dict, next_id: str) -> Text:
    widget = Text()
    widget.text = widget_json.get("text")

    widget.next_widget = next_id
    widget.current_widget = widget_json.get("id")

    return widget


def process_multiple_choice(widget_json: dict, edges, vertices) -> Question_MultipleChoice:
    widget = Question_MultipleChoice()

    choices_json = widget_json.get("children")
    choices = []

    for i, choice in enumerate(choices_json):
        choice_data = choice.get("value")
        id_ = choice.get("id")
        text = choice_data.get("text")
        score = choice_data.get("score")

        edge = edges[id_]
        next_vertex = vertices[edge.get("target")]
        next_widget_id = next_vertex.get("id")

        choices.append(Choice(
            text=text, score=score, next_widget=next_widget_id, number=i)
        )

    widget.question_text = widget_json.get("text")
    widget.answers = choices
    widget.current_widget = widget_json.get("id")
    return widget


def process_number_simple(widget_json: dict, next_id: str) -> Question_NumberSimple:
    widget = Question_NumberSimple()
    widget.question_text = widget_json.get("text")
    widget.min = widget_json.get("min")
    widget.max = widget_json.get("max")

    widget.next_widget = next_id
    widget.current_widget = widget_json.get("id")

    return widget


def process_scale(widget_json: dict, next_id: str) -> Question_NumberScale:
    widget = Question_NumberScale()
    widget.question_text = widget_json.get("text")
    scores_json = widget_json.get("children")
    scores: List[Score] = []

    for i, choice in enumerate(scores_json):
        choice_data = choice.get("value")
        start = choice.get("startValue")
        end = choice_data.get("endValue")
        score = choice_data.get("resultScore")

        scores.append(Score(
            start_value=start, end_value=end, result_score=score)
        )

    widget.scores = scores
    widget.next_widget = next_id
    widget.current_widget = widget_json.get("id")

    return widget


def set_care_plan_id(widgets: List[DbWidget], cp_id):
    for wd in widgets:
        wd.care_plan_id = cp_id


def process_widget(vertex: dict, next_widget_id: str, vertices: dict, edges: dict):
    widget_data = vertex.get("value")
    type_ = VertexTypes(int(widget_data.get("type")))
    question_type = VertexTypes(int(widget_data.get("questionType", 0)))

    print("LOG in process_widget")
    print("widget_data: {}, type_: {}, question_type: {}".format(widget_data, type_, question_type))
    print("Temp LOG for multiple choice: targeted type_: {}, targeted question_type: {}".format(VertexTypes.question, VertexTypes.multiple_choice))

    if type_ == VertexTypes.choices:
        return
    if type_ not in [VertexTypes.multiple_choice, VertexTypes.text,
                     VertexTypes.number_simple, VertexTypes.question]:
        raise Exception(f"Unknown widget type {type_}")

    if type_ == VertexTypes.text:
        widget = process_text(widget_data, next_widget_id)

    elif type_ == VertexTypes.question and question_type == VertexTypes.multiple_choice:
        print("Temp LOG: enters to run process_multiple_choice")
        widget = process_multiple_choice(widget_data, edges, vertices)

    elif type_ == VertexTypes.question and question_type == VertexTypes.scale:
        widget = process_scale(widget_data, next_widget_id)

    else:
        widget = process_number_simple(widget_data, next_widget_id)

    widget.name = type(widget).__name__ + str(random.randint(0, 10000))
    return widget


def process_first_widget(edges: dict, vertices: dict):
    key = next(iter(edges))
    first_vertex = vertices.get(key)
    first_widget = process_widget(first_vertex, edges[key].get("target"), vertices, edges)
    first_widget.is_start_widget = True

    return first_widget


def process_json(ui_json: list, care_plan_id: str) -> Dict[str, DbWidget]:
    edges, vertices = parse_json(ui_json)
    first_widget = process_first_widget(edges, vertices)
    widgets = {first_widget.current_widget: first_widget}
    processed_ids = []

    for edge in edges.values():
        curr_id = edge.get("target")
        if curr_id in processed_ids:
            continue

        next_edge = edges.get(curr_id, None)
        next_id = next_edge.get("target") if next_edge else None

        curr_vertex = vertices.get(curr_id)
        curr_widget = process_widget(curr_vertex, next_id,
                                     vertices, edges)
        if curr_widget:
            widgets[curr_widget.current_widget] = curr_widget
            processed_ids.append(curr_id)

    print("LOG Widgets from processed JSON: ", widgets)
    set_care_plan_id(list(widgets.values()), care_plan_id)

    return widgets


def save(widgets: List[DbWidget]):
    DbWidget.objects.insert(widgets)


if __name__ == '__main__':
    with open("../json/frontend_care_plan2.json", "r") as file:
        ui_json = json.load(file).get("graph")
        care_plan_id = "607dab7fcbff8531c843caf7"
        process_json(ui_json, care_plan_id)
