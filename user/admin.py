from django.contrib import admin
from django.utils.safestring import mark_safe
from django.contrib.auth.admin import UserAdmin as SuperUserAdmin
from user.models import User, StudentUser, UserPool, UserPoolHasUser, UserPoolHasAssessment


@admin.register(User)
class UserAdmin(SuperUserAdmin):
    list_display = (
        "username",
        "email",
        "name",
    )
    readonly_fields = ("uuid", "last_login", "date_joined", "change_password_link")

    @mark_safe
    def change_password_link(self, obj):
        return f"<a target='_blank' href='/admin/user/user/{obj.id}/password/'>Trocar Senha</a>"

    change_password_link.short_description = "Trocar Senha"
    change_password_link.allow_tags = True


@admin.register(StudentUser)
class StudentUserAdmin(UserAdmin):

    def get_queryset(self, request):
        qs = super(StudentUserAdmin, self).get_queryset(request)
        return qs.filter(is_staff=False, is_superuser=False)


class UserPoolHasUserInline(admin.TabularInline):
    model = UserPoolHasUser
    extra = 1


class UserPoolHasAssessmentInline(admin.TabularInline):
    model = UserPoolHasAssessment
    extra = 1


@admin.register(UserPool)
class UserPoolAdmin(admin.ModelAdmin):
    list_display = ("uuid", "name")
    readonly_fields = ("uuid",)
    inlines = (UserPoolHasAssessmentInline, UserPoolHasUserInline)
