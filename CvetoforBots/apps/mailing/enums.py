from django.db import models


class RecipientType(models.TextChoices):
    """Тип получателей рассылки"""
    NEW = 'NEW', 'Новые'
    ONE = 'ONE', 'Разовые покупатели'
    REGULAR = 'REGULAR', 'Постоянные'


class SendingStatus(models.TextChoices):
    """Перечисление статусов отправки рассылки"""
    SUCCESS = 'success', 'Отправлено успешно'
    ERROR = 'error', 'Ошибка при отправке'


class MailingType(models.TextChoices):
    """Перечисление тем рассылок"""

    PERSONAL_DISCOUNT = 'personal_discount', 'Персональные скидки'
    NEW_BOUQUETS = 'new_bouquets', 'Новые букеты / акции'
    HOLIDAY_OFFERS = 'holiday_offers', 'Праздничные предложения'
