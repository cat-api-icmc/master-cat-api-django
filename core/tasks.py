import json

from django.utils.text import slugify
from django.contrib.auth.hashers import make_password

from learning.models import (
    AssessmentType,
    Question,
    Alternative,
    QuestionParams,
    QuestionTag,
)
from learning.services import QuestionPoolService
from user.models import UserPool
from user.services import UserPoolService


def __upload_irt_questions_params(question_id: int, model: str, params: dict) -> None:
    QuestionParams.objects.create(
        model=model,
        question_id=question_id,
        irt_difficulty=params.get("difficulty", 0),
        irt_discrimination=params.get("discrimination", 1),
        irt_guess=params.get("guess", 0),
        irt_upper_asymptote=params.get("upper_asymptote", 0),
    )


def __upload_mirt_questions_params(question_id: int, model: str, params: dict) -> None:
    QuestionParams.objects.create(
        model=model,
        question_id=question_id,
        irt_difficulty=params.get("difficulty", 0),
        mirt_discrimination=params.get("discrimination", []),
        irt_guess=params.get("guess", 0),
        irt_upper_asymptote=params.get("upper_asymptote", 1),
    )


def __upload_cdm_questions_params(question_id: int, model: str, params: dict) -> None:
    QuestionParams.objects.create(
        model=model,
        question_id=question_id,
        cdm_slipping=params.get("slipping", 0),
        cdm_guessing=params.get("guessing", 0),
        cdm_qmatrix=params.get("qmatrix", []),
    )


def __upload_question(question_data: dict, model: str) -> Question:
    tag_id = (
        QuestionTag.objects.get_or_create(name=question_data["tag"])[0].id
        if "tag" in question_data
        else None
    )

    question = Question.objects.create(
        statement=question_data["statement"], tag_id=tag_id
    )

    Alternative.objects.bulk_create(
        [
            Alternative(
                question_id=question.id,
                text=alternative.get("text", ""),
                is_correct=alternative.get("is_correct", False),
            )
            for alternative in question_data.get("alternatives", [])
        ]
    )

    if AssessmentType.is_irt(model):
        __upload_irt_questions_params(question.id, model, question_data["params"])
    if AssessmentType.is_mirt(model):
        __upload_mirt_questions_params(question.id, model, question_data["params"])
    if AssessmentType.is_cdm(model):
        __upload_cdm_questions_params(question.id, model, question_data["params"])

    return question


def upload_questions_json(obj_file) -> int:
    data: dict = json.load(obj_file)
    model, questions = data["model"], data["questions"]

    questions_created = [__upload_question(data, model) for data in questions]

    pool = QuestionPoolService.create_pool(questions_created, super_pool=True)
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

    data: dict = xmltodict.parse(obj_file, encoding="utf-8")

    question_data = filter(
        lambda q: q.get("@type") == "multichoice",
        data.get("quiz", {}).get("question", []),
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

    pool = QuestionPoolService.create_pool(questions_created, super_pool=True)
    return len(pool)


def mass_create_users(obj_file) -> int:
    import pandas as pd
    from user.models import User

    EMAIL_DOMAIN = "@usp.br"

    columns = ["email_base", "full_name"]
    data = pd.read_csv(obj_file, usecols=columns, sep=";")

    def _get_pw(pw_base: str) -> str:
        return make_password(f"pw.{pw_base}")

    def _get_user(row) -> User:
        email_base, full_name = row["email_base"], row["full_name"]

        email = f"{email_base}{EMAIL_DOMAIN}"
        first_name, last_name = full_name.split(" ", 1)
        username = slugify(full_name).replace("-", "_")
        password = _get_pw(email_base)

        return User.objects.get_or_create(
            email=email,
            defaults={
                "first_name": first_name,
                "last_name": last_name,
                "username": username,
                "password": password,
                "is_active": True,
                "is_staff": False,
                "is_superuser": False,
            },
        )[0]

    users_created = [_get_user(row) for _, row in data.iterrows()]
    UserPoolService.create_user_pool(users_created)

    return len(users_created)
