from rest_framework.permissions import BasePermission, SAFE_METHODS


class UserPermission(BasePermission):

    def has_permission(self, request, view) -> bool:
        return bool(
            request.method in SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_active
        )


class AuthorStaffOrReadOnly(UserPermission):

    def has_object_permission(
        self, request, view, obj
    ) -> bool:
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_active
            and (request.user == obj.author or request.user.is_staff)
        )


class AdminOrReadOnly(UserPermission):

    def has_object_permission(
        self, request, view
    ) -> bool:
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_active
            and request.user.is_staff
        )


class OwnerUserOrReadOnly(UserPermission):

    def has_object_permission(
        self, request, view, obj
    ) -> bool:
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_active
            and request.user == obj.following
            or request.user.is_staff
        )
