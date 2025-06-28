import arrow
from rest_framework import viewsets, status
from rest_framework.response import Response
from core.permissions import HasAPIAccess
from plumber.client import PlumberClient
from .models import *
from .serializers import *
from .services import QuestionPoolService, UserAssessmentService
from .repositories import AssessmentRepository


class AssessmentViewset(viewsets.ModelViewSet):
    serializer_class = AssessmentSerializer
    permission_classes = [HasAPIAccess]
    lookup_field = "uuid"

    def get_queryset(self):
        return AssessmentRepository.get_active_assessments()

    def list(self, request, *args, **kwargs):
        qs = AssessmentRepository.get_user_assessments(request.user)
        data = AssessmentSerializer(qs, many=True).data
        return Response(data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, uuid=None, **kwargs):
        if assessment := AssessmentRepository.get_user_assessment(request.user, uuid):
            data = AssessmentSerializer(assessment).data
            return Response(data, status=status.HTTP_200_OK)
        return Response({}, status=status.HTTP_404_NOT_FOUND)


class UserAssessmentViewset(viewsets.ModelViewSet):
    serializer_class = None
    permission_classes = [HasAPIAccess]
    lookup_field = "uuid"

    def get_queryset(self):
        return UserAssessment.objects.filter(user_id=self.request.user.id)

    def create(self, request):
        assessment = Assessment.objects.filter(
            uuid=request.data.get("assessment")
        ).first()

        if not assessment:
            return Response(
                {"error": "Assessment not found."}, status=status.HTTP_404_NOT_FOUND
            )

        created = False
        user_assessment = UserAssessmentService.get_in_progress_assessment(
            request.user.id, assessment.id
        )

        if not user_assessment:
            user_assessment, success = UserAssessmentService.create(
                request.user.id, assessment
            )
            if not success:
                return Response(**user_assessment)
            created = True

        next_question = QuestionPoolService.get_next_question(
            assessment.pool_id, user_assessment.next_index
        )
        assesssment_data: dict = AssessmentSerializer(assessment).data

        data = {
            "user_assessment": user_assessment.uuid,
            "status": user_assessment.status,
            "next_question": QuestionSerializer(next_question).data,
            **assesssment_data,
        }

        return Response(
            data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )

    def update(self, request, uuid=None):
        payload = request.data.copy()

        user_assessment = (
            UserAssessment.objects.select_related("assessment")
            .filter(uuid=uuid)
            .first()
        )

        alternative = Alternative.objects.filter(
            uuid=payload.get("alternative")
        ).first()

        if not user_assessment or not alternative:
            return Response(
                {"error": "User assessment or alternative not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        plumb_code, plumb_response = PlumberClient().next_item(
            answer=int(alternative.is_correct),
            previous_index=user_assessment.next_index,
            encoded_design=user_assessment.design,
        )

        if plumb_code >= 400:
            return Response(plumb_response, status=plumb_code)

        user_assessment.next_index = plumb_response.get("next_index", 0)
        user_assessment.design = plumb_response.get("design", None)
        stop_assessment = plumb_response.get("stop", False)
        assessment_data: dict = AssessmentSerializer(user_assessment.assessment).data

        if stop_assessment:
            user_assessment.status = UserAssessment.COMPLETED
            user_assessment.finished = arrow.now().__str__()
            user_assessment.save(
                update_fields=["next_index", "design", "status", "finished"]
            )

            UserAssessmentService.get_design_data(user_assessment)

            data = {
                "user_assessment": user_assessment.uuid,
                "status": user_assessment.status,
                "next_question": None,
                **assessment_data,
            }

            return Response(data, status=status.HTTP_200_OK)

        user_assessment.save(update_fields=["next_index", "design"])

        next_question = (
            QuestionPoolHasQuestion.objects.select_related("question")
            .get(
                pool_id=user_assessment.assessment.pool_id,
                order=plumb_response.get("next_index"),
            )
            .question
        )

        data = {
            "user_assessment": user_assessment.uuid,
            "status": user_assessment.status,
            "next_question": QuestionSerializer(next_question).data,
            **assessment_data,
        }

        return Response(data, status=status.HTTP_200_OK)
