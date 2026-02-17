from django.contrib import admin
from django.utils.safestring import mark_safe
from core.tasks import (
    upload_questions_json,
    upload_questions_csv,
    upload_questions_mdl,
    mass_create_users,
)
from core.models import MassProcess, UploadQuestions


@admin.register(UploadQuestions)
class UploadQuestionsAdmin(admin.ModelAdmin):
    readonly_fields = ("examples",)

    JSON = "json"
    CSV = "csv"
    MOODLE = "mdl"

    FILE_EXTENSION_MAP = {
        JSON: upload_questions_json,
        CSV: upload_questions_csv,
        MOODLE: upload_questions_mdl,
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
            (
                "Exemplo JSON TRI",
                "json/upload-irt-questions-admin-example.json",
                "upload-questions.json",
            ),
            (
                "Exemplo JSON mTRI",
                "json/upload-mirt-questions-admin-example.json",
                "upload-questions.json",
            ),
            (
                "Exemplo JSON MDC",
                "json/upload-cdm-questions-admin-example.json",
                "upload-questions.json",
            ),
            (
                "Exemplo CSV",
                "csv/upload-questions-admin-example.csv",
                "upload-questions.csv",
            ),
            (
                "Exemplo Moodle",
                "mdl/upload-questions-admin-example.mdl",
                "upload-questions.mdl",
            ),
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


@admin.register(MassProcess)
class MassProcessAdmin(admin.ModelAdmin):
    readonly_fields = ("examples",)

    TASK_MAP = {
        MassProcess.CREATE_USERS: mass_create_users,
    }

    def has_change_permission(self, *args, **kwargs):
        return False

    def get_fieldsets(self, request, obj=None):
        if obj:
            return ((None, {"fields": ("uuid", "file", "type", "status", "result")}),)
        return ((None, {"fields": ("type", "file", "examples")}),)

    @mark_safe
    def examples(self, obj):

        EXAMPLES = [
            (f"Exemplo {v}", f"mass-process/{k}.csv", f"{k}.csv")
            for k, v in MassProcess.TYPE_CHOICES
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
        type = obj.type

        obj.status = MassProcess.PROCESSING
        obj.save()

        try:
            count = self.TASK_MAP[type](obj.file)
            obj.status = MassProcess.FINISHED
            obj.result = f"{count} objects created."
        except Exception as e:
            obj.status = MassProcess.ERROR
            obj.result = str(e)
        finally:
            obj.save()

    examples.short_description = "Exemplos"
    examples.allow_tags = True
