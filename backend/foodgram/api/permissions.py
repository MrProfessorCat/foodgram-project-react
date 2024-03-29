from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        if (
            request.method in permissions.SAFE_METHODS
            and request.user.is_active
        ):
            return True
        return request.user.is_staff

    def has_object_permission(self, request, view, obj):
        print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!222222')
        return request.method in permissions.SAFE_METHODS


class IsAdminAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user and request.user.is_active
            or request.user.is_staff
        )


class IsAuthenticatedAdminAuthorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if (
            request.method in permissions.SAFE_METHODS
            and request.user.is_authenticated
            and request.user.is_active
        ):
            return True

    def has_object_permission(self, request, view, obj):
        if (
            request.method in permissions.SAFE_METHODS
            and request.user.is_authenticated
            and request.user.is_active
        ):
            return True
        return (
            obj.author == request.user and request.user.is_active
            or request.user.is_staff
        )
