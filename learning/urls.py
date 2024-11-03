from rest_framework import routers
from django.conf.urls import include
from django.urls import path
from .views import *


router = routers.DefaultRouter()
router.register(r"assessment", AssessmentViewset, basename="assessment")
router.register(r"user-assessment", UserAssessmentViewset, basename="user-assessment")

urlpatterns = [
    path(r"api/", include(router.urls)),
]
