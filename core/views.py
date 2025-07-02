from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import connections, utils
from plumber.client import PlumberClient


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
    def __check_plumber_connection(self) -> tuple:
        return PlumberClient().health_check()

    @classmethod
    def __check(self, method) -> Response:
        chk, data = method()
        _status = status.HTTP_200_OK if chk else status.HTTP_500_INTERNAL_SERVER_ERROR
        return Response(data, status=_status)

    def list(self, request, *args, **kwargs):
        return Response({"status": "Healthy!"}, status=status.HTTP_200_OK)

    @action(methods=["get"], url_path="db", url_name="db", detail=False)
    def db(self, request, *args, **kwargs):
        return self.__check(self.__check_database_connection)

    @action(methods=["get"], url_path="plumber", url_name="plumber", detail=False)
    def plumber(self, request, *args, **kwargs):
        return self.__check(self.__check_plumber_connection)

    @action(methods=["get"], url_path="all", url_name="all", detail=False)
    def all(self, request, *args, **kwargs):
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
