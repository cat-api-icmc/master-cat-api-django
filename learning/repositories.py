import arrow
from learning.models import (
    Assessment,
    UserAssessment,
    MirtDesignData,
    QuestionPoolHasQuestion,
)
from user.models import User, UserPoolHasAssessment, UserPoolHasUser
from django.db.models import Q, OuterRef, Exists


class AssessmentRepository(object):

    @classmethod
    def get_active_assessments(cls):
        return Assessment.objects.filter(
            Q(active=True)
            & Q(Q(start__lte=arrow.now().__str__()) | Q(start__isnull=True))
            & Q(Q(finish__gte=arrow.now().__str__()) | Q(finish__isnull=True))
        )

    @classmethod
    def get_user_assessments(cls, user: User):
        qs = cls.get_active_assessments()
        if not user.is_superuser:
            user_pool_ids = UserPoolHasUser.objects.filter(
                user__id=user.id
            ).values_list("pool_id", flat=True)
            user_assessments = UserPoolHasAssessment.objects.filter(
                pool_id__in=user_pool_ids
            ).values_list("assessment_id", flat=True)
            qs = qs.filter(id__in=user_assessments)

        user_assessment_in_progress_qs = UserAssessment.objects.filter(
            user=user, assessment_id=OuterRef("id"), status=UserAssessment.IN_PROGRESS
        )
        qs = qs.annotate(in_progress=Exists(user_assessment_in_progress_qs))

        return (
            qs.filter(Q(retry=True) | Q(in_progress=False))
            if not user.is_superuser
            else qs
        )

    @classmethod
    def get_user_assessment(cls, user: User, assessment_uuid: str) -> Assessment:
        return cls.get_user_assessments(user).filter(uuid=assessment_uuid).first()


class MirtDesignDataRepository(object):

    @classmethod
    def designs_by_assessment(cls, assessment_id: int):
        return MirtDesignData.objects.select_related(
            "user_assessment", "user_assessment__user"
        ).filter(user_assessment__assessment_id=assessment_id)

    @classmethod
    def designs_by_user(cls, user_id: int):
        return MirtDesignData.objects.select_related("user_assessment").filter(
            user_assessment__user_id=user_id
        )
