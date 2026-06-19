from rest_framework import serializers
from learning.models import (
    AssessmentType,
    CriteriaTypes,
    Question,
    Alternative,
    Assessment,
    QuestionParams,
    ShadowTestConfig,
)


ASSESSMENT_CONFIG_FIELD_NAMES = (
    "type",
    "start_item",
    "criteria",
    "method",
    "thetas_start",
    "min_sem",
    "delta_thetas",
    "threshold",
    "min_items",
    "max_items",
    "max_time",
    "exposure_control",
    "exposure_values",
    "quadpts",
    "theta_range",
    "weights",
    "latent_means",
    "latent_covariances",
    "prior",
    "kl_delta",
    "model_type",
    "shadow_test_config"
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


class Irt1PLQuestionParamsPlumberSerializer(QuestionParamsPlumberSerializer):

    class Meta:
        model = QuestionParams
        fields = (
            "id",
            "irt_difficulty",
        )


class Irt2PLQuestionParamsPlumberSerializer(QuestionParamsPlumberSerializer):

    class Meta:
        model = QuestionParams
        fields = (
            "id",
            "irt_discrimination",
            "irt_difficulty",
        )


class Irt3PLQuestionParamsPlumberSerializer(QuestionParamsPlumberSerializer):

    class Meta:
        model = QuestionParams
        fields = (
            "id",
            "irt_discrimination",
            "irt_difficulty",
            "irt_guess",
        )


class Irt4PLQuestionParamsPlumberSerializer(QuestionParamsPlumberSerializer):

    class Meta:
        model = QuestionParams
        fields = (
            "id",
            "irt_discrimination",
            "irt_difficulty",
            "irt_guess",
            "irt_upper_asymptote",
        )


class Mirt1PLQuestionParamsPlumberSerializer(Irt1PLQuestionParamsPlumberSerializer):
    pass


class Mirt2PLQuestionParamsPlumberSerializer(QuestionParamsPlumberSerializer):
    irt_discrimination = serializers.ListField(source="mirt_discrimination")

    class Meta:
        model = QuestionParams
        fields = (
            "id",
            "irt_discrimination",
            "irt_difficulty",
        )


class Mirt3PLQuestionParamsPlumberSerializer(QuestionParamsPlumberSerializer):
    irt_discrimination = serializers.ListField(source="mirt_discrimination")

    class Meta:
        model = QuestionParams
        fields = (
            "id",
            "irt_discrimination",
            "irt_difficulty",
            "irt_guess",
        )


class Mirt4PLQuestionParamsPlumberSerializer(QuestionParamsPlumberSerializer):
    irt_discrimination = serializers.ListField(source="mirt_discrimination")
    
    class Meta:
        model = QuestionParams
        fields = (
            "id",
            "irt_discrimination",
            "irt_difficulty",
            "irt_guess",
            "irt_upper_asymptote",
        )


class DinaQuestionParamsPlumberSerializer(QuestionParamsPlumberSerializer):

    class Meta:
        model = QuestionParams
        fields = ("id", "cdm_slipping", "cdm_guessing", "cdm_qmatrix")


class DinoQuestionParamsPlumberSerializer(DinaQuestionParamsPlumberSerializer):
    pass


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
            AssessmentType.IRT_1PL: Irt1PLQuestionParamsPlumberSerializer,
            AssessmentType.IRT_2PL: Irt2PLQuestionParamsPlumberSerializer,
            AssessmentType.IRT_3PL: Irt3PLQuestionParamsPlumberSerializer,
            AssessmentType.IRT_4PL: Irt4PLQuestionParamsPlumberSerializer,
            AssessmentType.MIRT_2PL: Mirt2PLQuestionParamsPlumberSerializer,
            AssessmentType.MIRT_3PL: Mirt3PLQuestionParamsPlumberSerializer,
            AssessmentType.MIRT_4PL: Mirt4PLQuestionParamsPlumberSerializer,
            AssessmentType.CDM_DINA: DinaQuestionParamsPlumberSerializer,
            AssessmentType.CDM_DINO: DinoQuestionParamsPlumberSerializer,
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


class ShadowTestConfigSerializer(serializers.ModelSerializer):
    query = serializers.CharField(source="itens_query", read_only=True)
    op = serializers.CharField(source="operator", read_only=True)

    class Meta:
        model = ShadowTestConfig
        fields = ("query", "op", "value")


class AssessmentConfigSerializer(serializers.ModelSerializer):
    start_item = serializers.SerializerMethodField()
    min_sem = serializers.SerializerMethodField()
    delta_thetas = serializers.SerializerMethodField()
    thetas_start = serializers.SerializerMethodField()
    model_type = serializers.CharField(source="type")
    criteria = serializers.SerializerMethodField()
    shadow_test_config = ShadowTestConfigSerializer(many=True, read_only=True)
    theta_range = serializers.ListField(read_only=True, source="theta_range_values")

    class Meta:
        model = Assessment
        fields = ASSESSMENT_CONFIG_FIELD_NAMES

    def get_criteria(self, obj):
        return CriteriaTypes.KL if obj.criteria == CriteriaTypes.CDMKL else obj.criteria

    def get_start_item(self, obj):
        return obj.start_item or self.get_criteria(obj)

    def get_min_sem(self, obj):
        return obj.min_sem_value

    def get_delta_thetas(self, obj):
        return obj.delta_thetas_value

    def get_thetas_start(self, obj):
        return obj.thetas_start_value

class IRTAssessmentConfigSerializer(AssessmentConfigSerializer):

    class Meta:
        model = Assessment
        fields = ASSESSMENT_CONFIG_FIELD_NAMES


class CDMAssessmentConfigSerializer(AssessmentConfigSerializer):
    threshold = serializers.SerializerMethodField()

    class Meta:
        model = Assessment
        fields = ASSESSMENT_CONFIG_FIELD_NAMES + ("threshold",)

    def get_threshold(self, obj):
        return obj.threshold_value
