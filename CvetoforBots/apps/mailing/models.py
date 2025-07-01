from django.db import models

from CvetoforBots.apps.core.models import BotInstance
from CvetoforBots.apps.mailing.enums import MailingType, RecipientType, SendingStatus


class Mailing(models.Model):
    """Модель рассылки"""

    title = models.CharField(verbose_name="Заголовок", max_length=255, null=True, blank=True)
    body = models.TextField(verbose_name="Сообщение рассылки", null=True, blank=True)
    image = models.ImageField(verbose_name="Изображение рассылки", upload_to="mailings/", blank=True, null=True)
    bot = models.ForeignKey(BotInstance, verbose_name="Бот", on_delete=models.SET_NULL, null=True, blank=True, related_name="mailings")
    time_start = models.DateTimeField(verbose_name="Дата и время начала рассылки", blank=True, null=True)
    is_instant = models.BooleanField(verbose_name="Немедленная рассылка", default=False)
    recipient_type = models.CharField(verbose_name="Тип получателей", max_length=255, choices=RecipientType.choices)
    ready_to_send = models.BooleanField(verbose_name="Готова к отправке", default=False)
    theme = models.CharField(verbose_name="Тема рассылки", choices=MailingType.choices, max_length=255, null=True, blank=True)
    is_processed = models.BooleanField(verbose_name="В обработке", default=False)
    button_text = models.CharField(verbose_name="Текст кнопки", max_length=255, null=True, blank=True)
    button_link = models.CharField(verbose_name="Ссылка кнопки", max_length=255, null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"


class MailingLog(models.Model):
    """Модель лога попытки рассылки"""

    mail = models.ForeignKey(Mailing, verbose_name="Рассылка", on_delete=models.CASCADE, related_name="logs")
    user_id = models.CharField(verbose_name="ID пользователя", max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(verbose_name="Дата и время создания лога", auto_now_add=True)
    sending_status = models.CharField(verbose_name="Статус отправки", choices=SendingStatus.choices, default=None, null=True)
    error = models.TextField(verbose_name="Ошибка", null=True, blank=True)

    def __str__(self):
        return f"{self.sending_status} {self.user_id}"

    class Meta:
        verbose_name = "Лог рассылки"
        verbose_name_plural = "Логи рассылок"
