from django import forms

from learning.models import CriteriaTypes

class AssessmentForm(forms.ModelForm):
    
    def clean(self):
        pool = self.cleaned_data.get("pool")
        max_items = self.cleaned_data.get("max_items")
        min_items = self.cleaned_data.get("min_items")
        start_item = self.cleaned_data.get("start_item")
        criteria = self.cleaned_data.get("criteria")
        
        if criteria and start_item and criteria == CriteriaTypes.SEQ and start_item != 1:
            raise forms.ValidationError({
                "start_item": "O item inicial deve ser 1 para Critério de Seleção de Sequencial."
            })
        
        if pool:
            if max_items and max_items > len(pool):
                raise forms.ValidationError({
                    "max_items": "Máximo de items não pode ser maior que o número de questões no banco de questões."
                })
            if min_items and min_items > len(pool):
                raise forms.ValidationError({
                    "min_items": "Mínimo de items não pode ser maior que o número de questões no banco de questões."
                })
