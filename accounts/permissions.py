from rest_framework.permissions import BasePermission


class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser or request.user.is_staff:
            return True

        return obj == request.user


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj == request.user
