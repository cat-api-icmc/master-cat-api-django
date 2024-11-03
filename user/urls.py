from rest_framework import routers
from django.conf.urls import include
from django.urls import path
from .views import *


router = routers.DefaultRouter()
router.register(r"auth", UserAuthViewset, basename="user-auth")

urlpatterns = [
    path(r"api/", include(router.urls)),
]
