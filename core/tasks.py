import json
from learning.models import Question, Alternative
from learning.services import QuestionPoolService


def upload_questions_json(obj_file) -> int:
    data: dict = json.load(obj_file)
    key = next(iter(data.keys()))
    question_keys = ("statement", "discrimination", "difficulty", "guess")

    questions_created = []
    for question in data[key]:
        obj = Question.objects.create(**{k: question[k] for k in question_keys})
        Alternative.objects.bulk_create(
            [
                Alternative(
                    question=obj,
                    text=alternative.get("text", ""),
                    is_correct=question.get(f"is_correct", False),
                )
                for alternative in question.get("alternatives", [])
            ]
        )
        questions_created.append(obj)

    pool = QuestionPoolService.create_pool(questions_created, super=True)
    return len(pool)


def upload_questions_csv(obj_file) -> int:
    import pandas as pd

    return 0
