from django import forms

class AssessmentForm(forms.ModelForm):
    
    def clean(self):
        pool = self.cleaned_data.get("pool")
        max_items = self.cleaned_data.get("max_items")
        if pool and max_items and max_items > len(pool):
            raise forms.ValidationError({
                "max_items": "Máximo de items não pode ser maior que o número de questões no banco de questões."
            })
