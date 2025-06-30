from learning.models import Assessment, UserAssessment
from .extractors import *
from django.db.models import Model as DjangoModel


class BaseContext:
    obj_model = DjangoModel
    data_extractor_class = BaseDataExtractor

    def __init__(self, context_data: dict, lookup_field: str = "uuid"):
        self.data = context_data
        self.obj = self.obj_model.objects.get(
            **{lookup_field: self.data.get(lookup_field)}
        )
        self.data_extractor = self.data_extractor_class(self.obj)

    def __call__(self) -> dict:
        return self.data


class AssessmentResultContext(BaseContext):
    obj_model = Assessment
    data_extractor_class = AssessmentResultDataExtractor

    def charts_data(self) -> list:
        chart_functions = [
            self.data_extractor.average_time_per_question_chart,
            self.data_extractor.average_correct_answer_per_question_chart,
        ]
        return [(func.__name__, func()) for func in chart_functions]

    def questions_data(self) -> list:
        return self.data_extractor.questions_data()

    def students_data(self) -> list:
        return self.data_extractor.students_data()

    def __call__(self):
        return {
            **self.data,
            "assessment_name": self.obj.name,
            "assessment_id": self.obj.id,
            "charts": self.charts_data(),
            "questions": self.questions_data(),
            "students": self.students_data(),
        }


class AssessmentStudentDetailContext(BaseContext):
    obj_model = UserAssessment
    data_extractor_class = AssessmentStudentDetailDataExtractor

    def charts_data(self) -> list:
        chart_functions = [
            self.data_extractor.time_history_chart,
            self.data_extractor.response_history_chart,
            self.data_extractor.theta_history_chart,
            self.data_extractor.standard_error_history_chart,
        ]
        return [(func.__name__, func()) for func in chart_functions]

    def __call__(self):
        return {
            **self.data,
            "student": {
                "id": self.obj.user.id,
                "name": self.obj.user.name,
            },
            "assessment": {
                "id": self.obj.assessment.id,
                "name": self.obj.assessment.name,
            },
            "charts": self.charts_data(),
        }
