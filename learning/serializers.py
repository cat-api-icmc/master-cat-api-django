from rest_framework import serializers
from .models import (
    AssessmentConfig,
    AssessmentType,
    Question,
    Alternative,
    Assessment,
    QuestionParams,
)


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


class QuestionParamsPlumberSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="uuid", read_only=True)

    class Meta:
        model = QuestionParams
        fields = ("id",)


class IrtQuestionParamsPlumberSerializer(QuestionParamsPlumberSerializer):

    class Meta:
        model = QuestionParams
        fields = (
            "id",
            "irt_discrimination",
            "irt_difficulty",
            "irt_guess",
            "irt_upper_asymptote",
        )


class MirtQuestionParamsPlumberSerializer(QuestionParamsPlumberSerializer):

    class Meta:
        model = QuestionParams
        fields = ("id", "irt_mparams")


class DinQuestionParamsPlumberSerializer(QuestionParamsPlumberSerializer):

    class Meta:
        model = QuestionParams
        fields = ("id", "cdm_slipping", "cdm_guessing", "cdm_qmatrix")


class GdinaQuestionParamsPlumberSerializer(QuestionParamsPlumberSerializer):

    class Meta:
        model = QuestionParams
        fields = ("id", "cdm_mparams", "cdm_qmatrix")


class QuestionPlumberSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="uuid", read_only=True)
    order = serializers.SerializerMethodField()
    params = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ("id", "order", "params")

    def get_order(self, obj):
        return getattr(obj, "question_order", 0)

    @classmethod
    def __get_model_serializer(cls, model):
        switcher = {
            AssessmentType.IRT_1PL: IrtQuestionParamsPlumberSerializer,
            AssessmentType.IRT_2PL: IrtQuestionParamsPlumberSerializer,
            AssessmentType.IRT_3PL: IrtQuestionParamsPlumberSerializer,
            AssessmentType.IRT_4PL: IrtQuestionParamsPlumberSerializer,
            AssessmentType.MIRT_1PL: MirtQuestionParamsPlumberSerializer,
            AssessmentType.MIRT_2PL: MirtQuestionParamsPlumberSerializer,
            AssessmentType.MIRT_3PL: MirtQuestionParamsPlumberSerializer,
            AssessmentType.MIRT_4PL: MirtQuestionParamsPlumberSerializer,
            AssessmentType.CDM_DINA: DinQuestionParamsPlumberSerializer,
            AssessmentType.CDM_DINO: DinQuestionParamsPlumberSerializer,
            AssessmentType.CDM_GDINA: GdinaQuestionParamsPlumberSerializer,
        }
        return switcher[model]

    def get_params(self, obj):
        question_params = self.context.get("question_params", [])
        params_obj = next(
            (qp for qp in question_params if qp.question_id == obj.id), None
        )
        if params_obj:
            serializer_class = self.__get_model_serializer(params_obj.model)
            return serializer_class(params_obj).data
        return None


class AssessmentSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="uuid", read_only=True)

    class Meta:
        model = Assessment
        fields = ("id", "name", "fixed_question_count")



class AssessmentConfigSerializer(serializers.ModelSerializer):
    start_item = serializers.SerializerMethodField()
    min_sem = serializers.SerializerMethodField()
    delta_thetas = serializers.SerializerMethodField()
    thetas_start = serializers.SerializerMethodField()
    pattern_theta = serializers.SerializerMethodField()
    model_type = serializers.CharField(source="type")

    class Meta:
        model = Assessment
        fields = tuple(
            [field.name for field in AssessmentConfig._meta.fields] + ["model_type"]
        )

    def get_start_item(self, obj: AssessmentConfig):
        return obj.start_item or "random"

    def get_min_sem(self, obj: AssessmentConfig):
        return obj.min_sem_value

    def get_delta_thetas(self, obj: AssessmentConfig):
        return obj.delta_thetas_value

    def get_thetas_start(self, obj: AssessmentConfig):
        return obj.thetas_start_value

    def get_pattern_theta(self, obj: AssessmentConfig):
        return obj.pattern_theta_value
