from django.db.models import F
from learning.models import (
    Assessment,
    QuestionParams,
    QuestionPool,
    UserAssessment,
    MirtDesignData,
    QuestionPoolHasQuestion,
    Question,
)
from learning.serializers import AssessmentConfigSerializer, QuestionPlumberSerializer
from plumber.client import PlumberClient

class QuestionPoolService(object):

    @classmethod
    def get_next_question(cls, pool_id: int, index: int) -> Question:
        return QuestionPoolHasQuestion.objects.get(
            pool_id=pool_id, order=index
        ).question

    @classmethod
    def create_pool(cls, queryset: list, super_pool=False) -> QuestionPool:
        pool = QuestionPool.objects.create(name="_", super_pool=super_pool)

        qphq = [
            QuestionPoolHasQuestion(pool=pool, question=q, order=i + 1)
            for i, q in enumerate(queryset)
        ]
        QuestionPoolHasQuestion.objects.bulk_create(qphq)

        return pool.save_fields(name=f"Pool_{pool.id}_{pool.created}")


class UserAssessmentService(object):

    @classmethod
    def get_in_progress_assessment(
        cls, user_id: int, assessment_id: int
    ) -> UserAssessment:
        return UserAssessment.objects.filter(
            user_id=user_id,
            assessment_id=assessment_id,
            status=UserAssessment.IN_PROGRESS,
        ).first()

    @classmethod
    def create(
        cls, user_id: int, assessment: Assessment, user_thetas_start = None
    ) -> tuple[UserAssessment, bool]:
        questions = assessment.pool.questions.filter(
            questionpoolhasquestion__removed__isnull=True
        ).annotate(
            question_order=F("questionpoolhasquestion__order")
        ).order_by("questionpoolhasquestion__order")
        question_params = QuestionParams.objects.filter(
            question_id__in=(q.id for q in questions), model=assessment.type
        )

        questions_data = QuestionPlumberSerializer(
            questions, many=True, context={"question_params": question_params}
        ).data

        if user_thetas_start is not None:
            assessment.thetas_start = user_thetas_start

        assessment_config = AssessmentConfigSerializer(assessment).data

        start_function = (
            PlumberClient().cdm_start_assesment
            if assessment.is_cdm
            else PlumberClient().irt_start_assesment
        )
        plumb_code, plumb_response = start_function(questions_data, assessment_config)

        if plumb_code >= 400:
            return {"data": plumb_response, "status": plumb_code}, False

        user_assessment = UserAssessment.objects.create(
            user_id=user_id,
            assessment_id=assessment.id,
            status=UserAssessment.IN_PROGRESS,
            next_index=plumb_response.get("next_index", 0),
            design=plumb_response.get("design", None),
        )

        return user_assessment, True

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
