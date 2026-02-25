from turtle import st

import arrow
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from core.permissions import HasAPIAccess
from plumber.client import PlumberClient
from user.models import UserPoolHasUser
from learning.models import (
    Alternative,
    Assessment,
    QuestionPoolHasQuestion,
    UserAssessment,
)
from learning.serializers import (
    AssessmentSerializer,
    QuestionSerializer,
)
from learning.services import QuestionPoolService, UserAssessmentService
from learning.repositories import AssessmentRepository


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
        if assessment := AssessmentRepository.get_user_assessment(
            request.user, kwargs["uuid"]
        ):
            data = AssessmentSerializer(assessment).data
            return Response(data, status=status.HTTP_200_OK)
        return Response({}, status=status.HTTP_404_NOT_FOUND)


class UserAssessmentViewset(viewsets.ModelViewSet):
    serializer_class = None
    permission_classes = [HasAPIAccess]
    lookup_field = "uuid"

    def get_queryset(self):
        return UserAssessment.objects.filter(user_id=self.request.user.id)

    def create(self, request, *args, **kwargs):
        assessment = Assessment.objects.filter(
            uuid=request.data.get("assessment")
        ).first()

        if not assessment:
            return Response(
                {"error": "Assessment not found."}, status=status.HTTP_404_NOT_FOUND
            )

        user_pool = UserPoolHasUser.objects.filter(
            user_id=request.user.id,
            pool__userpoolhasassessment__assessment_id=assessment.id,
        ).first()

        if not user_pool:
            return Response(
                {"error": "User not enrolled in the assessment's pool."},
                status=status.HTTP_403_FORBIDDEN,
            )

        created = False
        user_assessment = UserAssessmentService.get_in_progress_assessment(
            request.user.id, assessment.id
        )

        if not user_assessment:
            user_assessment, success = UserAssessmentService.create(
                request.user.id, assessment, user_thetas_start=user_pool.thetas_start
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
            "in_progress": user_assessment.in_progress,
            "next_question": QuestionSerializer(next_question).data,
            **assesssment_data,
        }

        return Response(
            data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )

    def update(self, request, *args, **kwargs):
        payload = request.data.copy()

        user_assessment = (
            UserAssessment.objects.select_related("assessment")
            .filter(uuid=kwargs["uuid"])
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

        if user_assessment.assessment.is_cdm:
            plumb_code, plumb_response = PlumberClient().cdm_next_item(
                answer=int(alternative.is_correct),
                previous_index=user_assessment.next_index,
                encoded_design=user_assessment.design,
            )
        else:
            plumb_code, plumb_response = PlumberClient().irt_next_item(
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
                "in_progress": user_assessment.in_progress,
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
            "in_progress": user_assessment.in_progress,
            "next_question": QuestionSerializer(next_question).data,
            **assessment_data,
        }

        return Response(data, status=status.HTTP_200_OK)

    @action(
        methods=["POST"],
        detail=True,
        url_path="force-complete",
        url_name="force-complete",
    )
    def force_complete(self, request, uuid=None, **kwargs):
        user_assessment = UserAssessment.objects.filter(uuid=uuid).first()
        if not user_assessment:
            return Response(
                {"error": "User assessment not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        if user_assessment.status == UserAssessment.COMPLETED:
            return Response(
                {"error": "User assessment already completed."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user_assessment.save_fields(
            status=UserAssessment.COMPLETED, finished=arrow.now().__str__()
        )
        UserAssessmentService.get_design_data(user_assessment)
        return Response(
            {"message": "User assessment forcefully completed."},
            status=status.HTTP_200_OK,
        )
