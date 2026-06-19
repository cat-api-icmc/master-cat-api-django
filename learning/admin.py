import logging

from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils.html import format_html

from learning.forms import (
    AssessmentForm,
    QuestionBalancerInlineFormSet,
    QuestionParamsInlineForm,
)
from learning.services import QuestionPoolService
from learning.models import (
    Alternative,
    Assessment,
    Question,
    QuestionBalancer,
    QuestionParams,
    QuestionPool,
    QuestionPoolHasQuestion,
    QuestionSuperPool,
    QuestionTag,
    ShadowTestConfig,
)
from user.models import UserPoolHasAssessment


logger = logging.getLogger(__name__)


@admin.register(QuestionTag)
class QuestionTagAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = ("name", "id", "uuid")
    readonly_fields = ("id", "uuid")


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
    list_display = ("uuid", "id", "__str__", "tag")
    readonly_fields = ("id", "uuid")
    actions = ["create_pool"]
    inlines = [AlternativeInline, QuestionParamsInline]
    raw_id_fields = ("tag",)
    fieldsets = (
        (None, {"fields": ("id", "uuid", "tag")}),
        ("Conteúdo", {"fields": ("statement",)}),
    )

    def create_pool(self, _request, queryset):
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


class QuestionBalancerInline(admin.TabularInline):
    raw_id_fields = ("question_tag",)
    model = QuestionBalancer
    extra = 1
    formset = QuestionBalancerInlineFormSet


class ShadowTestConfigInline(admin.TabularInline):
    model = ShadowTestConfig
    extra = 1


class UserPoolHasAssessmentInline(admin.TabularInline):
    model = UserPoolHasAssessment
    extra = 1


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    form = AssessmentForm
    list_display = ("name", "id", "uuid", "active", "pool", "dashboards")
    raw_id_fields = ("pool",)
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
                ),
            },
        ),
        (
            "CONFIGURAÇÕES DO TESTE",
            {
                "fields": [
                    "type",
                    "method",
                    "criteria",
                    "start_item",
                    "thetas_start",
                    "quadpts",
                    "theta_range",
                    "weights",
                    "latent_means",
                    "latent_covariances",
                    "prior",
                    "kl_delta",
                ]
            },
        ),
        (
            "CRITÉRIOS DE PARADA",
            {
                "fields": [
                    "min_items",
                    "max_items",
                    "min_sem",
                    "delta_thetas",
                    "threshold",
                    "max_time",
                ]
            },
        ),
        (
            "CONTROLE DE EXPOSIÇÃO",
            {
                "fields": ["exposure_control", "exposure_values"],
            },
        ),
    )
    inlines = [
        QuestionBalancerInline,
        ShadowTestConfigInline,
        UserPoolHasAssessmentInline,
    ]

    class Media:
        js = ("admin/js/assessment_admin.js",)

    def save_model(self, request, obj, form, change):
        try:
            super().save_model(request, obj, form, change)
        except (ValidationError, IntegrityError) as exc:
            logger.exception(
                "AssessmentAdmin.save_model failed: assessment_id=%s, name=%r, change=%s, exception=%s, form_errors=%s, non_field_errors=%s",
                getattr(obj, "pk", None),
                getattr(obj, "name", None),
                change,
                exc,
                form.errors.as_json() if hasattr(form, "errors") else None,
                list(form.errors.get("__all__", [])) if hasattr(form, "errors") else None,
            )
            raise
        except Exception as exc:  # noqa: BLE001
            logger.exception(
                "AssessmentAdmin.save_model unexpected failure: assessment_id=%s, name=%r, change=%s, exception=%s, form_errors=%s, non_field_errors=%s",
                getattr(obj, "pk", None),
                getattr(obj, "name", None),
                change,
                exc,
                form.errors.as_json() if hasattr(form, "errors") else None,
                list(form.errors.get("__all__", [])) if hasattr(form, "errors") else None,
            )
            raise

    def save_related(self, request, form, formsets, change):
        try:
            super().save_related(request, form, formsets, change)
        except (ValidationError, IntegrityError) as exc:
            logger.exception(
                "AssessmentAdmin.save_related failed: assessment_id=%s, name=%r, change=%s, exception=%s, form_errors=%s, non_field_errors=%s",
                getattr(form.instance, "pk", None),
                getattr(form.instance, "name", None),
                change,
                exc,
                form.errors.as_json() if hasattr(form, "errors") else None,
                list(form.errors.get("__all__", [])) if hasattr(form, "errors") else None,
            )
            for formset in formsets:
                non_form_errors = getattr(formset, "non_form_errors", None)
                non_form_errors = list(non_form_errors()) if callable(non_form_errors) else None
                logger.error(
                    "AssessmentAdmin.related formset state: formset=%s, errors=%s, non_form_errors=%s",
                    formset.__class__.__name__,
                    getattr(formset, "errors", None),
                    non_form_errors,
                )
            raise
        except Exception as exc:  # noqa: BLE001
            logger.exception(
                "AssessmentAdmin.save_related unexpected failure: assessment_id=%s, name=%r, change=%s, exception=%s, form_errors=%s, non_field_errors=%s",
                getattr(form.instance, "pk", None),
                getattr(form.instance, "name", None),
                change,
                exc,
                form.errors.as_json() if hasattr(form, "errors") else None,
                list(form.errors.get("__all__", [])) if hasattr(form, "errors") else None,
            )
            for formset in formsets:
                non_form_errors = getattr(formset, "non_form_errors", None)
                non_form_errors = list(non_form_errors()) if callable(non_form_errors) else None
                logger.error(
                    "AssessmentAdmin.related formset state: formset=%s, errors=%s, non_form_errors=%s",
                    formset.__class__.__name__,
                    getattr(formset, "errors", None),
                    non_form_errors,
                )
            raise

    def dashboards(self, obj):
        return format_html(
            '<div><a href="/data/assessment/{}/result" target="_blank">Resultados</a></div>',
            obj.uuid,
        )

    dashboards.short_description = "Dashboards"
