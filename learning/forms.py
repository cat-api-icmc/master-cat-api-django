import re
from django import forms

from learning.models import AssessmentType, CriteriaTypes, QuestionParams


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
            raise forms.ValidationError(
                f"A soma dos pesos deve ser 1.0 (atual: {total:.4f})."
            )


class AssessmentForm(forms.ModelForm):

    def __validate_start_item(self) -> None:
        start_item = self.cleaned_data.get("start_item")
        criteria = self.cleaned_data.get("criteria")
        if start_item and criteria == CriteriaTypes.SEQ and start_item != 1:
            raise forms.ValidationError(
                {
                    "start_item": "O item inicial deve ser 1 para Critério de Seleção de Sequencial."
                }
            )

    def __validate_max_min_items(self) -> None:
        pool = self.cleaned_data.get("pool")
        max_items = self.cleaned_data.get("max_items")
        min_items = self.cleaned_data.get("min_items")

        if not pool:
            return

        if max_items and max_items > len(pool):
            raise forms.ValidationError(
                {
                    "max_items": "Máximo de items não pode ser maior que o número de questões no banco de questões."
                }
            )

        if min_items and min_items > len(pool):
            raise forms.ValidationError(
                {
                    "min_items": "Mínimo de items não pode ser maior que o número de questões no banco de questões."
                }
            )

    def __validate_threshold(self) -> None:
        threshold = self.cleaned_data.get("threshold")
        model = self.cleaned_data.get("model")

        if not threshold or not model:
            return

        if not AssessmentType.is_cdm(model):
            raise forms.ValidationError(
                {"threshold": "Threshhold só pode ser definido para modelos CDM."}
            )

        # Accept either a single float or two floats separated by comma/space
        threshold_str = str(threshold).strip()
        # Match a single float or two floats (comma or space separated)
        pattern = r"^\s*-?\d+(\.\d+)?(\s*[, ]\s*-?\d+(\.\d+)?\s*)?$"
        if not re.match(pattern, threshold_str):
            raise forms.ValidationError(
                {
                    "threshold": "Threshhold deve ser um número ou dois números separados por vírgula ou espaço."
                }
            )

    def __validate_theta_range(self) -> None:
        theta_range = self.cleaned_data.get("theta_range")
        model = self.cleaned_data.get("model")

        if not theta_range or not model:
            return

        if not AssessmentType.is_irt(model) and not AssessmentType.is_mirt(model):
            raise forms.ValidationError(
                {
                    "theta_range": "Theta range só pode ser definido para modelos IRT ou MIRT."
                }
            )

        # Accept two floats separated by comma/space
        theta_range_str = str(theta_range).strip()
        pattern = r"^\s*-?\d+(\.\d+)?\s*[, ]\s*-?\d+(\.\d+)?\s*$"
        if not re.match(pattern, theta_range_str):
            raise forms.ValidationError(
                {
                    "theta_range": "Theta range deve ser dois números separados por vírgula ou espaço."
                }
            )

        # Validate that the first number is less than the second number
        parts = re.split(r"[, ]", theta_range_str)
        if len(parts) == 2:
            try:
                low = float(parts[0].strip())
                high = float(parts[1].strip())
                if low >= high:
                    raise forms.ValidationError(
                        {
                            "theta_range": "O primeiro número do theta range deve ser menor que o segundo número."
                        }
                    )
            except ValueError:
                raise forms.ValidationError(
                    {"theta_range": "Theta range deve conter números válidos."}
                )

    def clean(self):
        self.__validate_start_item()
        self.__validate_max_min_items()
        self.__validate_threshold()
        self.__validate_theta_range()
        return super().clean()
