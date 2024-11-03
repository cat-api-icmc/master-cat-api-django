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


class AssessmentConfigSerializer(serializers.ModelSerializer):
    min_sem = serializers.SerializerMethodField()
    delta_thetas = serializers.SerializerMethodField()
    thetas_start = serializers.SerializerMethodField()
    pattern_theta = serializers.SerializerMethodField()

    class Meta:
        model = Assessment
        fields = tuple([field.name for field in AssessmentConfig._meta.fields])
    
    def get_min_sem(self, obj: AssessmentConfig):
        return obj.min_sem_value
    
    def get_delta_thetas(self, obj: AssessmentConfig):
        return obj.delta_thetas_value
    
    def get_thetas_start(self, obj: AssessmentConfig):
        return obj.thetas_start_value
    
    def get_pattern_theta(self, obj: AssessmentConfig):
        return obj.pattern_theta_value
