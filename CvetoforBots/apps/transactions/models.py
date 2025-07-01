from django.db import models
from solo.models import SingletonModel

from CvetoforBots.apps.core.models import TelegramUser
from CvetoforBots.apps.orders.models import Order
from CvetoforBots.apps.transactions.enums import PaymentStatus


class Transaction(models.Model):
    """Модель платежа."""

    user = models.ForeignKey(TelegramUser, verbose_name="Пользователь", on_delete=models.SET_NULL, related_name="transactions", null=True)
    payment_id = models.CharField(verbose_name="ID платежа", max_length=255, null=True)
    amount = models.IntegerField(verbose_name="Сумма платежа")
    created_at = models.DateTimeField(verbose_name="Дата создания", auto_now_add=True)
    description = models.CharField(verbose_name="Описание платежа", max_length=255, null=True)
    status = models.CharField(
        verbose_name="Статус платежа", choices=PaymentStatus.choices, default=PaymentStatus.NEW, max_length=255
    )
    order = models.ForeignKey(Order, verbose_name="Заказ", on_delete=models.DO_NOTHING, null=True)
    idempotence_key = models.CharField(verbose_name="Ключ идемпотентности", max_length=255, null=True)
    error_description = models.CharField(verbose_name="Описание ошибки", max_length=255, null=True)

    def __str__(self):
        return f"№ {self.id}"

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"


class AmoCRM(SingletonModel):
    """Модель настроек AmoCRM."""

    refresh_token = models.TextField(default=None, null=True, blank=True)
    access_token = models.TextField(default=None, null=True, blank=True)
