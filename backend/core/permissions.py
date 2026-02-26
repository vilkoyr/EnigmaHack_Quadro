from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Доступ только для администраторов."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and getattr(request.user, 'role', None) == 'admin'


class IsAdminOrAgent(permissions.BasePermission):
    """Админ или сотрудник техподдержки."""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role in ('admin', 'agent')


class CanEditProcessedData(permissions.BasePermission):
    """Редактирование обращений: админ или назначенный агент."""
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        if request.user.role == 'agent' and obj.assignee_id == request.user.id:
            return True
        return False


class CanManageComments(permissions.BasePermission):
    """Удаление комментария: автор или админ."""
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        return obj.author_id == request.user.id
