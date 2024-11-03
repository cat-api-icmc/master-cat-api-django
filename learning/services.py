from learning.models import (
    QuestionPool,
    UserAssessment,
    MirtDesignData,
    QuestionPoolHasQuestion,
    Question,
)
from plumber.client import PlumberClient


class QuestionPoolService(object):

    @classmethod
    def get_next_question(cls, pool_id: int, index: int) -> Question:
        return QuestionPoolHasQuestion.objects.get(
            pool_id=pool_id, order=index
        ).question

    @classmethod
    def create_pool(cls, queryset: list, super=False) -> QuestionPool:
        pool = QuestionPool.objects.create(name="_", super_pool=super)

        qphq = [
            QuestionPoolHasQuestion(pool=pool, question=q, order=i + 1)
            for i, q in enumerate(queryset)
        ]
        QuestionPoolHasQuestion.objects.bulk_create(qphq)

        return pool.save_fields(name=f"Pool_{pool.id}_{pool.created}")


class UserAssessmentService(object):

    @classmethod
    def get_design_data(
        cls, user_assessment: UserAssessment, clear_design: bool = False
    ) -> MirtDesignData:
        design_data = PlumberClient().get_design_data(user_assessment.design)

        if clear_design:
            user_assessment.save_fields(design=None)

        return MirtDesignData.objects.create(
            user_assessment_id=user_assessment.id, **design_data
        )
