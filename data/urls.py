from django.urls import re_path
from django.contrib.auth.decorators import login_required
from .views import *

urlpatterns = [
    re_path(
        r"^assessment/(?P<uuid>[0-9A-Za-z_\-]+)/result",
        login_required(AssessmentResultView.as_view()),
        name="assessment-feedback",
    ),
    re_path(
        r"^assessment/student/(?P<uuid>[0-9A-Za-z_\-]+)/detail",
        login_required(AssessmentStudentDetailView.as_view()),
        name="assessment-feedback",
    ),
]
