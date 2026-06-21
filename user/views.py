import uuid
import arrow
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from user.models import User, UserToken
from user.serializers import SimpleUserSerializer


USER_LOGIN_REQUEST_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=["email", "password"],
    properties={
        "email": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
        "password": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD),
    },
)

USER_LOGIN_RESPONSE_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "token": openapi.Schema(type=openapi.TYPE_STRING),
        "user_id": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID),
    },
)

ERROR_RESPONSE_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "error": openapi.Schema(type=openapi.TYPE_STRING),
    },
)


class UserAuthViewset(viewsets.GenericViewSet):

    def get_serializer(self, *args, **kwargs):
        return None

    @swagger_auto_schema(
        operation_summary="Autentica o usuário",
        tags=["Auth"],
        request_body=USER_LOGIN_REQUEST_SCHEMA,
        responses={
            200: openapi.Response("Token criado", USER_LOGIN_RESPONSE_SCHEMA),
            400: openapi.Response("Credenciais inválidas", ERROR_RESPONSE_SCHEMA),
        },
    )
    @action(methods=["POST"], detail=False, url_path="login", url_name="login")
    def login(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        user = User.objects.filter(email=email).first()
        if not user or not user.check_password(password):
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST
            )

        user.save_fields(last_login=arrow.now().__str__())

        token, _ = UserToken.objects.get_or_create(
            user=user, defaults={"token": uuid.uuid4().__str__()}
        )
        data = {
            "token": token.token,
            "user_id": user.uuid,
        }
        return Response(data, status=status.HTTP_200_OK)


class UserMeViewset(viewsets.ModelViewSet):
    serializer_class = SimpleUserSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return User.objects.none()
        if not getattr(self, "request", None) or not getattr(self.request, "user", None):
            return User.objects.none()
        return User.objects.filter(id=self.request.user.id, is_active=True)

    @swagger_auto_schema(
        operation_summary="Retorna os dados do usuário autenticado",
        tags=["Me"],
        responses={200: SimpleUserSerializer},
    )
    def list(self, request, *args, **kwargs):
        data = self.get_serializer(request.user).data
        return Response(data, status=status.HTTP_200_OK)
