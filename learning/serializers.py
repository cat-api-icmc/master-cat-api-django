from rest_framework import serializers
from .models import AssessmentConfig, Question, Alternative, Assessment


class AlternativeSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="uuid", read_only=True)

    class Meta:
        model = Alternative
        fields = ("id", "text")


class QuestionSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="uuid", read_only=True)
    alternatives = AlternativeSerializer(many=True)

    class Meta:
        model = Question
        fields = ("id", "statement", "alternatives")


class QuestionPlumberSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="uuid", read_only=True)

    class Meta:
        model = Question
        fields = ("id", "discrimination", "difficulty", "guess")


class AssessmentSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="uuid", read_only=True)

    class Meta:
        model = Assessment
        fields = ("id", "name")


class AssessmentConfigSerializer(serializers.Serializer):

    class Meta:
        model = Assessment
        fields = [
            (
                field.name + "_values"
                if field.name in ["min_sem", "delta_thetas", "thetas_start"]
                else ""
            )
            for field in AssessmentConfig._meta.fields
        ]
