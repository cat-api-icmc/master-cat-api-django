from django.db.models import Model as DjangoModel
from learning.models import Assessment, AssessmentType, UserAssessment
from data.extractors import (
    BaseDataExtractor,
    AssessmentResultDataExtractor,
    AssessmentStudentDetailIrtDataExtractor,
    AssessmentStudentDetailCdmDataExtractor,
)


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
    irt_extractor_class = AssessmentStudentDetailIrtDataExtractor
    cdm_extractor_class = AssessmentStudentDetailCdmDataExtractor

    def __init__(self, context_data: dict):
        super().__init__(context_data)
        extractor_class = (
            self.cdm_extractor_class
            if AssessmentType.is_cdm(self.obj.assessment.type)
            else self.irt_extractor_class
        )
        self.data_extractor = extractor_class(self.obj)

    def questions_data(self) -> list:
        return self.data_extractor.questions_data()

    def charts_data(self) -> list:
        return self.data_extractor.charts_data()

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
                "type": self.obj.assessment.type,
            },
            "questions": self.questions_data(),
            "charts": self.charts_data(),
        }
