from rest_framework import routers
from django.conf.urls import include
from django.urls import path
from .views import *


router = routers.DefaultRouter()
router.register(r"hc", HealthCheck, basename="health-check")

urlpatterns = [
    path(r"api/", include(router.urls)),
]
