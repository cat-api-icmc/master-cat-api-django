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

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class UserAssessmentViewset(viewsets.ModelViewSet):
    serializer_class = None
    permission_classes = [HasAPIAccess]
    lookup_field = "uuid"

    def get_queryset(self):
        return UserAssessmentViewset.objects.filter(user_id=self.request.user.id)

    def create(self, request):
        assessment = Assessment.objects.get(uuid=request.data.get("assessment"))
        questions = assessment.pool.questions.all().order_by(
            "questionpoolhasquestion__order"
        )

        questions_data = QuestionPlumberSerializer(questions, many=True).data

        assessment_config = AssessmentConfigSerializer(assessment).data

        plumb_code, plumb_response = PlumberClient().start_assesment(
            questions_data, assessment_config
        )

        if plumb_code >= 400:
            return Response(plumb_response, status=plumb_code)

        user_assessment, _ = UserAssessment.objects.update_or_create(
            user_id=request.user.id,
            assessment_id=assessment.id,
            defaults=dict(
                next_index=plumb_response.get("next_index", 0),
                design=plumb_response.get("design", None),
            ),
        )

        next_question = QuestionPoolService.get_next_question(
            assessment.pool_id, plumb_response.get("next_index")
        )
        assesssment_data: dict = AssessmentSerializer(assessment).data

        data = {
            "user_assessment": user_assessment.uuid,
            "status": UserAssessment.IN_PROGRESS,
            "next_question": QuestionSerializer(next_question).data,
            **assesssment_data,
        }

        return Response(data, status=status.HTTP_200_OK)

    def update(self, request, uuid=None):
        user_assessment = UserAssessment.objects.select_related("assessment").get(
            uuid=uuid
        )
        payload = request.data.copy()

        alternative = Alternative.objects.get(uuid=payload.get("alternative"))

        plumb_response = PlumberClient().next_item(
            answer=int(alternative.is_correct),
            previous_index=user_assessment.next_index,
            encoded_design=user_assessment.design,
        )

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

            payload = {
                "user_assessment": user_assessment.uuid,
                "status": UserAssessment.COMPLETED,
                "next_question": None,
                **assessment_data,
            }

            return Response(payload, status=status.HTTP_200_OK)

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
            "status": UserAssessment.IN_PROGRESS,
            "next_question": QuestionSerializer(next_question).data,
            **assessment_data,
        }

        return Response(data, status=status.HTTP_200_OK)
