class NotAddObjectPermissionMixin:
    """Запрет добавления объекта."""

    def has_add_permission(self, request, obj=None):
        return False


class NotChangeObjectPermissionMixin:
    """Запрет изменения объекта."""

    def has_change_permission(self, request, obj=None):
        return False


class NotDeleteObjectPermissionMixin:
    """Запрет удаления объекта."""

    def has_delete_permission(self, request, obj=None):
        return False


class NotAnyObjectPermissionMixin(
    NotAddObjectPermissionMixin,
    NotChangeObjectPermissionMixin,
    NotDeleteObjectPermissionMixin,
):
    """Запрет добавления, изменения, удаления объекта."""
