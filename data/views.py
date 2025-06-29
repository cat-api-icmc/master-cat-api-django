from django.views.generic import TemplateView
from .contexts import *


class BaseView(TemplateView):
    template_name: str = None
    context_class: BaseContext = None

    def get_context_data(self, **kwargs):
        return self.context_class(super().get_context_data(**kwargs))()


class AssessmentResultView(BaseView):
    template_name = "data/assessment_result.html"
    context_class = AssessmentResultContext
