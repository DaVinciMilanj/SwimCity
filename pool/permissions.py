from rest_framework.permissions import BasePermission


class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser or request.user.is_staff:
            return True

        return obj == request.user


class IsStudentOrNone(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.status == 'student' or request.user.status is None:
            return obj.request
