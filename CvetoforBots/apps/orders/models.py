from django.db import models

from CvetoforBots.apps.core.models import BotInstance, TelegramUser
from CvetoforBots.apps.orders.enums import OrderStatus, TimeIntervalEnum


class Order(models.Model):
    """Модель заказа товаров"""

    telegram_user = models.ForeignKey(TelegramUser, verbose_name="Пользователь", on_delete=models.SET_NULL, related_name="orders", null=True)
    user_name = models.CharField(verbose_name="Имя пользователя", max_length=100)
    user_contact = models.CharField(verbose_name="Контакт пользователя", max_length=100)
    recipient_name = models.CharField(verbose_name="Имя получателя", max_length=100)
    recipient_phone = models.CharField(verbose_name="Телефон получателя", max_length=100)
    recipient_address = models.CharField(verbose_name="Адрес получателя", max_length=255, default="-")
    delivery_date = models.DateField(verbose_name="Дата доставки", null=True, blank=True)
    time_interval = models.CharField(verbose_name="Время доставки", max_length=100, choices=TimeIntervalEnum.choices, null=True, blank=True)
    status = models.CharField(verbose_name="Статус", max_length=100, choices=OrderStatus.choices, default=OrderStatus.NEW)
    amount = models.DecimalField(verbose_name="Сумма", decimal_places=2, max_digits=8)
    with_post_card = models.BooleanField(verbose_name="С открыткой", default=False)
    post_card_text = models.TextField(verbose_name="Текст открытки", blank=True, null=True)
    bot_instance = models.ForeignKey(BotInstance, verbose_name="Бот", on_delete=models.SET_NULL, related_name="orders", null=True)
    group_product_id = models.IntegerField(verbose_name="Товар", null=True)
    created_at = models.DateTimeField(verbose_name="Дата создания", auto_now_add=True, null=True)
    lead_id = models.IntegerField(verbose_name="ID сделки AmoCRM", null=True, blank=True, default=None)
    compound = models.TextField(verbose_name="Состав заказа", null=True, blank=True)

    def __str__(self):
        return f"{self.telegram_user} {self.amount} {self.status}"

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
