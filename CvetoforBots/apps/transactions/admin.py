from django.contrib import admin
from solo.admin import SingletonModelAdmin

from CvetoforBots.apps.transactions.models import AmoCRM, Transaction
from CvetoforBots.apps.transactions.permissions import NotAnyObjectPermissionMixin


@admin.register(Transaction)
class TransactionAdmin(NotAnyObjectPermissionMixin, admin.ModelAdmin):
    ordering = ("-created_at",)
    list_filter = ("created_at", "status")
    search_fields = ("user__username", "user__telegram_id", "payment_id")
    search_help_text = "Поиск по Telegram ID или Telegram Username пользователя, названию квеста или идентификатору платежа"
    list_display = ("__str__", "user", "created_at", "amount", "status")
    readonly_fields = ("created_at",)


@admin.register(AmoCRM)
class AmoCRMAdmin(SingletonModelAdmin):
    pass
