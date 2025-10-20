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
            AssessmentType.MIRT_1PL: ["irt_mparams"],
            AssessmentType.MIRT_2PL: ["irt_mparams"],
            AssessmentType.MIRT_3PL: ["irt_mparams"],
            AssessmentType.MIRT_4PL: ["irt_mparams"],
            AssessmentType.CDM_DINA: ["cdm_slipping", "cdm_guessing", "cdm_qmatrix"],
            AssessmentType.CDM_DINO: ["cdm_slipping", "cdm_guessing", "cdm_qmatrix"],
            AssessmentType.CDM_GDINA: ["cdm_mparams", "cdm_qmatrix"],
        }
        _fields = default_fields + (
            fields_map.get(self.instance.model) if self.instance.pk else []
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


class AssessmentForm(forms.ModelForm):

    def clean(self):
        pool = self.cleaned_data.get("pool")
        max_items = self.cleaned_data.get("max_items")
        min_items = self.cleaned_data.get("min_items")
        start_item = self.cleaned_data.get("start_item")
        criteria = self.cleaned_data.get("criteria")

        if (
            criteria
            and start_item
            and criteria == CriteriaTypes.SEQ
            and start_item != 1
        ):
            raise forms.ValidationError(
                {
                    "start_item": "O item inicial deve ser 1 para Critério de Seleção de Sequencial."
                }
            )

        if pool:
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
