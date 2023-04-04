from rest_framework.permissions import BasePermission


class CreateUserPermissions(BasePermission):
    """
        Создавать новых пользователей, т.е. регистрироваться на сайте
        может только администратор и неавторизованный пользователь
    """
    def has_permission(self, request, view):
        return not request.user.is_authenticated or request.user.is_staff
