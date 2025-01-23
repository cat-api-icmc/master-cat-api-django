from learning.models import Question, Alternative
from learning.services import QuestionPoolService


def upload_questions_json(obj_file) -> int:
    import json
    
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

def upload_questions_mdl(obj_file) -> int:
    import xmltodict
    from urllib.parse import quote
    
    def _handle_statement(question_text: dict) -> str:
        statement: str = question_text.get("text", "")
        
        if "file" in question_text:
            file_name = question_text.get("file").get("@name", "")
            file_data = question_text.get("file").get("#text", "")
            statement = statement.replace(
                f"@@PLUGINFILE@@/{quote(file_name)}",
                f"data:image/png;base64,{file_data}",
            )
        
        return statement
    
    data: dict = xmltodict.parse(obj_file, encoding='utf-8')
    
    question_data = filter(
        lambda q: q.get("@type") == "multichoice",
        data.get("quiz", {}).get("question", [])
    )
    
    questions_created = []
    for question in question_data:
        obj = Question.objects.create(
            statement=_handle_statement(question.get("questiontext", {})),
        )
        Alternative.objects.bulk_create(
            [
                Alternative(
                    question=obj,
                    text=alternative.get("text", ""),
                    is_correct=bool(int(alternative.get("@fraction", "0"))),
                )
                for alternative in question.get("answer", [])
            ]
        )
        questions_created.append(obj)
    
    pool = QuestionPoolService.create_pool(questions_created, super=True)
    return len(pool)
