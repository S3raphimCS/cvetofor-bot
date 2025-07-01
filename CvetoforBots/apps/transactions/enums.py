from django.db import models


class PaymentStatus(models.TextChoices):
    """Статус платежа."""

    NEW = "new", "Новый"
    SUCCESS = "success", "Успешно"
    ERROR = "error", "Ошибка"
