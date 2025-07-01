from django.db import models


class OrderStatus(models.TextChoices):
    """Статус платежа."""

    NEW = "new", "Новый"
    PAID = "paid", "Оплачен"
    IN_WORK = "in_work", "В сборке"
    DONE = "done", "Завершен"
    CANCELED = "canceled", "Отменен"


class CityEnum(models.TextChoices):
    """Возможные города"""

    ULAN_UDE = "ulan_ude", "Улан-Удэ"
    ANGARSK = "angarsk", "Ангарск"


class TimeIntervalEnum(models.TextChoices):
    """Интервалы времени для доставки"""

    FROM_NINE_TO_TWELVE = "09:00-12:00", "09:00-12:00"
    FROM_TWELVE_TO_FIFTEEN = "12:00-15:00", "12:00-15:00"
    FROM_FIFTEEN_TO_EIGHTEEN = "15:00-18:00", "15:00-18:00"
    FROM_EIGHTEEN_TO_TWENTY_ONE = "18:00-21:00", "18:00-21:00"
    FROM_TWENTY_ONE_TO_TWENTY_THREE = "21:00-23:00", "21:00-23:00"
