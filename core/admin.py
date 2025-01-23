from core.tasks import upload_questions_json, upload_questions_csv
from .models import UploadQuestions
from django.contrib import admin
from django.utils.safestring import mark_safe


@admin.register(UploadQuestions)
class UploadQuestionsAdmin(admin.ModelAdmin):
    readonly_fields = ("examples",)

    JSON = "json"
    CSV = "csv"

    FILE_EXTENSION_MAP = {
        JSON: upload_questions_json,
        CSV: upload_questions_csv,
    }

    def has_change_permission(self, *args, **kwargs):
        return False

    def get_fieldsets(self, request, obj=None):
        if obj:
            return ((None, {"fields": ("uuid", "file", "status", "result")}),)
        return ((None, {"fields": ("file", "examples")}),)

    @mark_safe
    def examples(self, obj):
        EXAMPLES = [
            ("Exemplo JSON", "json/upload-questions-admin-exaple.json", "upload-questions.json"),
            ("Exemplo CSV", "csv/upload-questions-admin-exaple.csv", "upload-questions.csv"),
            ("Exemplo Moodle", "mdl/upload-questions-admin-exaple.mdl", "upload-questions.mdl"),
        ]
        return f"""
            <div>
                {'<br>'.join([
                    f'<a href="/static/dev/{path}" download="{file}">{name}</a>' 
                    for name, path, file in EXAMPLES]
                )}
            </div>
        """

    def save_model(self, request, obj, form, change):
        name = obj.file.name
        ext = name.split(".")[-1]

        obj.status = UploadQuestions.PROCESSING
        obj.save()

        try:
            count = self.FILE_EXTENSION_MAP[ext](obj.file)

            obj.status = UploadQuestions.FINISHED
            obj.result = f"{count} questions uploaded."
        except Exception as e:
            obj.status = UploadQuestions.ERROR
            obj.result = str(e)
        finally:
            obj.save()

    examples.short_description = "Exemplos"
    examples.allow_tags = True
