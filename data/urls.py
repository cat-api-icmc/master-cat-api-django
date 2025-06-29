from django.urls import re_path
from django.contrib.auth.decorators import login_required
from .views import *

urlpatterns = [
   re_path(
        r'^assessment/(?P<uuid>[0-9A-Za-z_\-]+)/result', 
        login_required(AssessmentResultView.as_view()), 
        name='assessment-feedback'
    ),
]
