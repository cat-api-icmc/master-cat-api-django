from learning.models import Assessment
from data.extractors import AssessmentResultDataExtractor

assessment = Assessment.objects.get(id=21)
extractor = AssessmentResultDataExtractor(assessment)

data = extractor.average_time_per_question_chart()
