import logging
import re
from django import forms

from learning.models import AssessmentType, CriteriaTypes, QuestionParams


logger = logging.getLogger(__name__)


class QuestionParamsInlineForm(forms.ModelForm):

    class Meta:
        model = QuestionParams
        fields = "__all__"

    def __setup_fields(self):
        default_fields = ["model"]
        fields_map = {
            AssessmentType.IRT_1PL: ["irt_difficulty"],
            AssessmentType.IRT_2PL: ["irt_difficulty", "irt_discrimination"],
            AssessmentType.IRT_3PL: [
                "irt_difficulty",
                "irt_discrimination",
                "irt_guess",
            ],
            AssessmentType.IRT_4PL: [
                "irt_difficulty",
                "irt_discrimination",
                "irt_guess",
                "irt_upper_asymptote",
            ],
            AssessmentType.MIRT_2PL: ["irt_difficulty", "mirt_discrimination"],
            AssessmentType.MIRT_3PL: [
                "irt_difficulty",
                "mirt_discrimination",
                "irt_guess",
            ],
            AssessmentType.MIRT_4PL: [
                "irt_difficulty",
                "mirt_discrimination",
                "irt_guess",
                "irt_upper_asymptote",
            ],
            AssessmentType.CDM_DINA: ["cdm_slipping", "cdm_guessing", "cdm_qmatrix"],
            AssessmentType.CDM_DINO: ["cdm_slipping", "cdm_guessing", "cdm_qmatrix"],
            AssessmentType.CDM_GDINA: ["cdm_mparams", "cdm_qmatrix"],
        }
        _fields = default_fields + (
            fields_map.get(self.instance.model, []) if self.instance.pk else []
        )
        for f in self.fields:
            if f not in _fields:
                self.fields[f].widget = forms.HiddenInput()
                self.fields[f].required = False
        if self.instance.pk:
            self.fields["model"].disabled = True
        else:
            self.fields["model"].initial = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__setup_fields()


class QuestionBalancerInlineFormSet(forms.BaseInlineFormSet):

    def clean(self):
        super().clean()
        cleaned_forms = [
            form
            for form in self.forms
            if form.cleaned_data and not form.cleaned_data.get("DELETE", False)
        ]
        if not cleaned_forms:
            return
        total = sum(form.cleaned_data.get("weight", 0) for form in cleaned_forms)
        if abs(total - 1.0) > 0.0001:
            logger.warning(
                "QuestionBalancerInlineFormSet validation failed: total weight=%.4f",
                total,
            )
            raise forms.ValidationError(
                f"A soma dos pesos desta seção deve ser 1.0. Valor atual: {total:.4f}."
            )


class AssessmentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "prior" in self.fields:
            self.fields["prior"].required = False

    def clean(self):
        cleaned_data = super().clean()
        summary_messages = []

        def register_error(field_name: str, message: str) -> None:
            self.add_error(field_name, message)
            summary_messages.append(f"{field_name}: {message}")

        start_item = cleaned_data.get("start_item")
        criteria = cleaned_data.get("criteria")
        if start_item and criteria == CriteriaTypes.SEQ and start_item != 1:
            register_error(
                "start_item",
                "O item inicial deve ser 1 quando o critério de seleção for Sequencial.",
            )

        pool = cleaned_data.get("pool")
        max_items = cleaned_data.get("max_items")
        min_items = cleaned_data.get("min_items")
        pool_size = len(pool) if pool else None

        if pool:
            if max_items and max_items > pool_size:
                register_error(
                    "max_items",
                    f"O máximo de itens não pode ser maior que o tamanho do banco de questões ({pool_size}).",
                )

            if min_items and min_items > pool_size:
                register_error(
                    "min_items",
                    f"O mínimo de itens não pode ser maior que o tamanho do banco de questões ({pool_size}).",
                )

        threshold = cleaned_data.get("threshold")
        assessment_type = cleaned_data.get("type")
        if assessment_type and AssessmentType.is_cdm(assessment_type):
            threshold_str = str(threshold).strip() if threshold is not None else ""
            pattern = r"^\s*-?\d+(\.\d+)?(\s*[, ]\s*-?\d+(\.\d+)?\s*)?$"
            if not threshold_str:
                register_error(
                    "threshold",
                    "O threshold é obrigatório para modelos CDM.",
                )
            elif not re.match(pattern, threshold_str):
                register_error(
                    "threshold",
                    "O threshold deve ser um número ou dois números separados por vírgula ou espaço.",
                )

        theta_range = cleaned_data.get("theta_range")
        if assessment_type and (
            AssessmentType.is_irt(assessment_type) or AssessmentType.is_mirt(assessment_type)
        ):
            theta_range_str = str(theta_range).strip() if theta_range is not None else ""
            pattern = r"^\s*-?\d+(\.\d+)?\s*[, ]\s*-?\d+(\.\d+)?\s*$"
            theta_parts = []
            if not theta_range_str:
                register_error(
                    "theta_range",
                    "O theta range é obrigatório para modelos IRT ou MIRT.",
                )
            elif not re.match(pattern, theta_range_str):
                register_error(
                    "theta_range",
                    "O theta range deve ter dois números separados por vírgula ou espaço.",
                )
            else:
                theta_parts = re.split(r"[, ]", theta_range_str)

            if len(theta_parts) == 2:
                try:
                    low = float(theta_parts[0].strip())
                    high = float(theta_parts[1].strip())
                    if low >= high:
                        register_error(
                            "theta_range",
                            "O primeiro número do theta range deve ser menor que o segundo número.",
                        )
                except ValueError:
                    register_error(
                        "theta_range",
                        "O theta range deve conter números válidos.",
                    )

        prior = cleaned_data.get("prior")
        if assessment_type and AssessmentType.is_cdm(assessment_type):
            if not prior:
                register_error(
                    "prior",
                    "A distribuição a priori é obrigatória para modelos CDM.",
                )
            elif not isinstance(prior, dict):
                register_error(
                    "prior",
                    "A distribuição a priori deve ser um objeto JSON válido.",
                )
            elif not prior:
                register_error(
                    "prior",
                    "A distribuição a priori não pode ser vazia para modelos CDM.",
                )

        if summary_messages:
            logger.warning(
                "AssessmentForm validation failed for %s: %s",
                getattr(self.instance, "pk", None) or "new-assessment",
                " | ".join(summary_messages),
            )

        return cleaned_data
