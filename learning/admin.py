from django.contrib import admin
from django.utils.safestring import mark_safe

from learning.forms import AssessmentForm
from learning.services import QuestionPoolService
from .models import *


class AlternativeInline(admin.TabularInline):
    model = Alternative
    extra = 1


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    search_fields = ("uuid", "statement")
    list_filter = ("pools",)
    list_display = ("uuid", "id", "__str__")
    readonly_fields = ("id", "uuid")
    actions = ["create_pool"]
    inlines = [AlternativeInline]
    fieldsets = (
        (None, {"fields": ("id", "uuid")}),
        ("Parâmetros IRT", {"fields": [f.name for f in IRTParams._meta.fields]}),
        ("Parâmetros CDM", {"fields": [f.name for f in CDMParams._meta.fields]}),
        ("Conteúdo", {"fields": ("statement",)}),
    )

    def create_pool(self, request, queryset):
        QuestionPoolService.create_pool(queryset)

    create_pool.short_description = "Criar Banco de Questões"


class QuestionInline(admin.TabularInline):
    model = QuestionPoolHasQuestion
    fields = ("question",)
    extra = 1


@admin.register(QuestionPool)
class QuestionPoolAdmin(admin.ModelAdmin):
    list_filter = ("super_pool",)
    list_display = ("name", "id", "uuid", "get_count")
    readonly_fields = ("id", "uuid", "get_count")
    inlines = [QuestionInline]
    fieldsets = ((None, {"fields": ("id", "uuid", "name", "super_pool")}),)

    def get_count(self, obj):
        return len(obj)

    get_count.short_description = "# Questões"


@admin.register(QuestionSuperPool)
class QuestionSuperPoolAdmin(QuestionPoolAdmin):
    list_filter = []

    def get_queryset(self, request):
        qs = super(QuestionSuperPoolAdmin, self).get_queryset(request)
        return qs.filter(super_pool=True)


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    form = AssessmentForm
    list_display = ("name", "id", "uuid", "active", "pool")
    readonly_fields = ("id", "uuid")
    fieldsets = (
        (None, {"fields": ("id", "uuid", "name", "active", "start", "finish", "pool")}),
        ("Configurações", {"fields": [f.name for f in AssessmentConfig._meta.fields]}),
    )


@admin.register(MirtDesignData)
class MirtDesignDataAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {"fields": ("user", "assessment")}),
        (
            "Info",
            {
                "fields": (
                    "item_history",
                    "response_history",
                    "theta_history",
                    "standard_error_history",
                    "summary",
                )
            },
        ),
    )
    
    @mark_safe
    def summary(self, obj):
        item_history = [(
            ih, 
            obj.response_history[ih-1],
            obj.theta_history[i+1],
            obj.standard_error_history[i+1],
        ) for i, ih in enumerate(obj.item_history) if ih != 'NA']
        return f'''
        <table>
            <tr>
                <th>Item</th>
                <th>Resposta</th>
                <th>Theta</th>
                <th>Erro Padrão</th>
            </tr>
            {
                ''.join([
                    f'<tr><td>{ih}</td><td>{r}</td><td>{t}</td><td>{se}</td></tr>' 
                    for ih, r, t, se in item_history
                ])
            }
        </table>
        '''

    def user(self, obj):
        return obj.user_assessment.user.__str__()

    def assessment(self, obj):
        return obj.user_assessment.assessment.__str__()

    def has_change_permission(self, *args, **kwargs):
        return False
    
    summary.short_description = "Resumo da Avaliação"
    summary.allow_tags = True
