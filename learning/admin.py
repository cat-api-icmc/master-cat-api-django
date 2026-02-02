from django.contrib import admin
from django.utils.safestring import mark_safe

from learning.forms import AssessmentForm, QuestionParamsInlineForm
from learning.services import QuestionPoolService
from user.models import UserPoolHasAssessment
from .models import (
    Alternative,
    Assessment,
    AssessmentConfig,
    MirtDesignData,
    Question,
    QuestionParams,
    QuestionPool,
    QuestionPoolHasQuestion,
    QuestionSuperPool,
)


class AlternativeInline(admin.TabularInline):
    model = Alternative
    extra = 1


class QuestionParamsInline(admin.StackedInline):
    model = QuestionParams
    extra = 0
    form = QuestionParamsInlineForm


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    search_fields = ("uuid", "statement")
    list_filter = ("pools",)
    list_display = ("uuid", "id", "__str__")
    readonly_fields = ("id", "uuid")
    actions = ["create_pool"]
    inlines = [AlternativeInline, QuestionParamsInline]
    fieldsets = (
        (None, {"fields": ("id", "uuid")}),
        ("Conteúdo", {"fields": ("statement",)}),
    )

    def create_pool(self, request, queryset):
        QuestionPoolService.create_pool(queryset)

    create_pool.short_description = "Criar Banco de Questões"


class QuestionInline(admin.TabularInline):
    model = QuestionPoolHasQuestion
    fields = ("question", "order")
    extra = 1
    raw_id_fields = ("question",)


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


class UserPoolHasAssessmentInline(admin.TabularInline):
    model = UserPoolHasAssessment
    extra = 1


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    form = AssessmentForm
    list_display = ("name", "id", "uuid", "active", "pool")
    readonly_fields = ("id", "uuid", "dashboards")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "id",
                    "uuid",
                    "name",
                    "active",
                    "retry",
                    "start",
                    "finish",
                    "pool",
                    "dashboards",
                )
            },
        ),
        ("Configurações", {"fields": [f.name for f in AssessmentConfig._meta.fields]}),
    )
    inlines = [UserPoolHasAssessmentInline]
    
    class Media:
        js = ('admin/js/assessment_admin.js',)

    @mark_safe
    def dashboards(self, obj):
        return f"""
            <div>
                <a href="/data/assessment/{obj.uuid}/result">Resultados</a>
            </div>
        """

    dashboards.short_description = "Dashboards"
    dashboards.allow_tags = True


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
    def summary(self, obj: MirtDesignData):
        item_history = [
            (
                ih,
                obj.response_history[ih - 1],
                obj.theta_history[i + 1],
                obj.standard_error_history[i + 1],
                obj.item_time_history[i],
            )
            for i, ih in enumerate(obj.item_history)
            if ih != "NA"
        ]

        contents = "".join(
            [
                f"""
            <tr>
                <td>{ih}</td>
                <td>{r}</td>
                <td>{t}</td>
                <td>{se}</td>
                <td>{it:.2f}</td>
            </tr>
        """
                for ih, r, t, se, it in item_history
            ]
        )

        return f"""
        <table>
            <tr>
                <th>Item</th>
                <th>Resposta</th>
                <th>Theta</th>
                <th>Erro Padrão</th>
                <th>Tempo de Resposta (s)</th>
            </tr>
            {contents}
        </table>
        """

    def user(self, obj):
        return obj.user_assessment.user.__str__()

    def assessment(self, obj):
        return obj.user_assessment.assessment.__str__()

    def has_change_permission(self, *args, **kwargs):
        return False

    summary.short_description = "Resumo da Avaliação"
    summary.allow_tags = True
