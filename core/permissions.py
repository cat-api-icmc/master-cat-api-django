from rest_framework import permissions


class HasAPIAccess(permissions.BasePermission):
    message = "Invalid or missing API Key."

    def has_permission(self, request, view):
        if user := getattr(request, "_user"):
            request.user = user
        return bool(request.user and request.user.is_active)
