from django.db import models


class Dashboard(models.Model):
    """Пустая модель для дашборда в админке"""
    class Meta:
        managed = False
        verbose_name = "Статистика бота"
        verbose_name_plural = "Статистика бота"
