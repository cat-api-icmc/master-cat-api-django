from learning.models import Assessment
from .extractors import AssessmentResultDataExtractor


class BaseContext:

    def __init__(self, context_data: dict):
        self.data = context_data

    def __call__(self) -> dict:
        return self.data


class AssessmentResultContext(BaseContext):

    def __init__(self, context_data):
        super().__init__(context_data)
        self.assessment = Assessment.objects.get(uuid=self.data.get("uuid"))
        self.data_extractor = AssessmentResultDataExtractor(self.assessment)

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
            "assessment_name": self.assessment.name,
            "assessment_id": self.assessment.id,
            "charts": self.charts_data(),
            "questions": self.questions_data(),
            "students": self.students_data(),
        }
