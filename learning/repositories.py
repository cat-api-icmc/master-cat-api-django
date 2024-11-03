import arrow
from learning.models import Assessment
from user.models import User, UserPoolHasAssessment, UserPoolHasUser
from django.db.models import Q


class AssessmentRepository(object):

    @classmethod
    def get_active_assessments(cls):
        return Assessment.objects.filter(
            Q(active=True)
            & Q(Q(start__lte=arrow.now().__str__()) | Q(start__isnull=True))
            & Q(finish__gte=arrow.now().__str__() | Q(finish__isnull=True))
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
        return qs
