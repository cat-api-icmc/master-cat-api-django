from learning.models import Assessment


class BaseContext:

    def __init__(self, context_data: dict):
        self.data = context_data

    def __call__(self) -> dict:
        return self.data


class AssessmentResultContext(BaseContext):

    def __call__(self):
        assessment = Assessment.objects.get(uuid=self.data.get("uuid"))

        return {
            **self.data,
            "assessment_name": assessment.name,
            "assessment_id": assessment.id,
        }
