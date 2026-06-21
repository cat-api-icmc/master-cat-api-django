from django.views.generic import TemplateView
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import connections, utils
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from plumber.client import PlumberClient


class HomeView(TemplateView):
    template_name = "home.html"


HEALTH_RESPONSE_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "status": openapi.Schema(type=openapi.TYPE_STRING),
    },
)

HEALTH_ALL_RESPONSE_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "status": openapi.Schema(type=openapi.TYPE_BOOLEAN),
        "rest-api": openapi.Schema(type=openapi.TYPE_STRING),
        "satabase": openapi.Schema(type=openapi.TYPE_OBJECT),
        "plumber-api": openapi.Schema(type=openapi.TYPE_OBJECT),
    },
)


class HealthCheck(viewsets.GenericViewSet):

    def get_serializer(self, *args, **kwargs):
        return None

    @classmethod
    def __check_database_connection(cls) -> tuple:
        try:
            with connections["default"].cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
                mysql_version = cursor.connection.get_server_info()
            return True, {"status": f"Healthy! {mysql_version}"}
        except utils.OperationalError:
            return False, {"status": "Unhealthy!"}

    @classmethod
    def __check_plumber_connection(cls) -> tuple:
        return PlumberClient().health_check()

    @classmethod
    def __check(cls, method) -> Response:
        chk, data = method()
        _status = status.HTTP_200_OK if chk else status.HTTP_500_INTERNAL_SERVER_ERROR
        return Response(data, status=_status)

    @swagger_auto_schema(
        operation_summary="Verifica a saúde da API",
        tags=["Health Check"],
        responses={200: openapi.Response("API saudável", HEALTH_RESPONSE_SCHEMA)},
    )
    def list(self, _request):
        return Response({"status": "Healthy!"}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Verifica a conexão com o banco",
        tags=["Health Check"],
        responses={
            200: openapi.Response("Banco saudável", HEALTH_RESPONSE_SCHEMA),
            500: openapi.Response("Falha ao conectar no banco", HEALTH_RESPONSE_SCHEMA),
        },
    )
    @action(methods=["get"], url_path="db", url_name="db", detail=False)
    def db(self, _request):
        return self.__check(self.__check_database_connection)

    @swagger_auto_schema(
        operation_summary="Verifica a integração com o Plumber",
        tags=["Health Check"],
        responses={
            200: openapi.Response("Plumber saudável", HEALTH_RESPONSE_SCHEMA),
            500: openapi.Response("Falha ao conectar no Plumber", HEALTH_RESPONSE_SCHEMA),
        },
    )
    @action(methods=["get"], url_path="plumber", url_name="plumber", detail=False)
    def plumber(self, _request):
        return self.__check(self.__check_plumber_connection)

    @swagger_auto_schema(
        operation_summary="Verifica todas as integrações",
        tags=["Health Check"],
        responses={
            200: openapi.Response("Tudo saudável", HEALTH_ALL_RESPONSE_SCHEMA),
            500: openapi.Response("Uma ou mais integrações falharam", HEALTH_ALL_RESPONSE_SCHEMA),
        },
    )
    @action(methods=["get"], url_path="all", url_name="all", detail=False)
    def all(self, _request):
        db_chk, db_data = self.__check_database_connection()
        plumber_chk, plumber_data = self.__check_plumber_connection()
        status_ok = db_chk and plumber_chk
        _status = (
            status.HTTP_200_OK if status_ok else status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        payload = {
            "status": status_ok,
            "rest-api": "Healthy!",
            "satabase": db_data,
            "plumber-api": plumber_data,
        }
        return Response(payload, status=_status)
