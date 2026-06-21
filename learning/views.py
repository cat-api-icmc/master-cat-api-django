import arrow
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
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


QUESTION_ALT_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "id": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID),
        "text": openapi.Schema(type=openapi.TYPE_STRING),
    },
)

QUESTION_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "id": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID),
        "statement": openapi.Schema(type=openapi.TYPE_STRING),
        "alternatives": openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=QUESTION_ALT_SCHEMA,
        ),
    },
)

USER_ASSESSMENT_REQUEST_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=["assessment"],
    properties={
        "assessment": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID),
    },
)

USER_ANSWER_REQUEST_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=["alternative"],
    properties={
        "alternative": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID),
    },
)

USER_ASSESSMENT_FLOW_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "user_assessment": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID),
        "status": openapi.Schema(type=openapi.TYPE_STRING),
        "in_progress": openapi.Schema(type=openapi.TYPE_BOOLEAN),
        "next_question": QUESTION_SCHEMA,
        "id": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID),
        "name": openapi.Schema(type=openapi.TYPE_STRING),
        "fixed_question_count": openapi.Schema(type=openapi.TYPE_INTEGER),
    },
)

ERROR_RESPONSE_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "error": openapi.Schema(type=openapi.TYPE_STRING),
    },
)

MESSAGE_RESPONSE_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "message": openapi.Schema(type=openapi.TYPE_STRING),
    },
)


class AssessmentViewset(viewsets.ModelViewSet):
    serializer_class = AssessmentSerializer
    permission_classes = [HasAPIAccess]
    lookup_field = "uuid"

    def get_queryset(self):
        return AssessmentRepository.get_active_assessments()

    @swagger_auto_schema(
        operation_summary="Lista as avaliações do usuário",
        tags=["Assessments"],
        responses={
            200: AssessmentSerializer(many=True),
            403: openapi.Response("Acesso negado", ERROR_RESPONSE_SCHEMA),
        },
    )
    def list(self, request, *args, **kwargs):
        qs = AssessmentRepository.get_user_assessments(request.user)
        data = AssessmentSerializer(qs, many=True).data
        return Response(data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Detalha uma avaliação do usuário",
        tags=["Assessments"],
        responses={
            200: AssessmentSerializer,
            404: openapi.Response("Avaliação não encontrada", ERROR_RESPONSE_SCHEMA),
        },
    )
    def retrieve(self, request, *args, **kwargs):
        if assessment := AssessmentRepository.get_user_assessment(
            request.user, kwargs["uuid"]
        ):
            data = AssessmentSerializer(assessment).data
            return Response(data, status=status.HTTP_200_OK)
        return Response({}, status=status.HTTP_404_NOT_FOUND)


class UserAssessmentViewset(viewsets.ModelViewSet):
    serializer_class = AssessmentSerializer
    permission_classes = [HasAPIAccess]
    lookup_field = "uuid"

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return UserAssessment.objects.none()
        return UserAssessment.objects.filter(user_id=self.request.user.id)

    @swagger_auto_schema(
        operation_summary="Cria ou retoma uma avaliação do usuário",
        tags=["User Assessments"],
        request_body=USER_ASSESSMENT_REQUEST_SCHEMA,
        responses={
            200: openapi.Response("Avaliação retomada", USER_ASSESSMENT_FLOW_SCHEMA),
            201: openapi.Response("Avaliação criada", USER_ASSESSMENT_FLOW_SCHEMA),
            403: openapi.Response("Usuário não matriculado", ERROR_RESPONSE_SCHEMA),
            404: openapi.Response("Avaliação não encontrada", ERROR_RESPONSE_SCHEMA),
        },
    )
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

    @swagger_auto_schema(
        operation_summary="Processa a resposta do usuário e avança a avaliação",
        tags=["User Assessments"],
        request_body=USER_ANSWER_REQUEST_SCHEMA,
        responses={
            200: openapi.Response("Resposta processada", USER_ASSESSMENT_FLOW_SCHEMA),
            404: openapi.Response("Avaliação ou alternativa não encontrada", ERROR_RESPONSE_SCHEMA),
        },
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
    @swagger_auto_schema(
        operation_summary="Finaliza uma avaliação manualmente",
        tags=["User Assessments"],
        responses={
            200: openapi.Response("Avaliação finalizada", MESSAGE_RESPONSE_SCHEMA),
            400: openapi.Response("Avaliação já finalizada", ERROR_RESPONSE_SCHEMA),
            404: openapi.Response("Avaliação não encontrada", ERROR_RESPONSE_SCHEMA),
        },
    )
    def force_complete(self, _request, uuid=None, **_kwargs):
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
