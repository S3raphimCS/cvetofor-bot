from django.contrib.sites.models import Site
from django.db import models
from django.urls import reverse

from CvetoforBots.common.models import BaseModel


class BotInstance(models.Model):
    STATUS_CHOICES = [
        ('running', 'Запущен'),
        ('stopped', 'Остановлен'),
        ('error', 'Ошибка'),
    ]
    title = models.CharField(
        verbose_name="Имя бота",
        max_length=100,
        blank=True,
    )
    token = models.CharField(
        verbose_name="Telegram Токен",
        max_length=100,
        unique=True
    )
    status = models.CharField(
        verbose_name="Статус бота",
        max_length=20,
        choices=STATUS_CHOICES,
        default='stopped',
    )
    started_at = models.DateTimeField(
        verbose_name="Запущен:",
        null=True,
        blank=True
    )
    down_at = models.DateTimeField(
        verbose_name="Остановлен:",
        null=True,
        blank=True
    )
    pid = models.IntegerField(
        verbose_name="PID",
        null=True,
        blank=True
    )
    cover = models.ImageField(
        verbose_name="Обложка бота",
        upload_to="covers/",
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = "Бот"
        verbose_name_plural = "Боты"

    def __str__(self):
        return f"{self.id} ---> {self.title}"


class TelegramUser(BaseModel):
    telegram_id = models.BigIntegerField(
        unique=True,
        verbose_name="Telegram ID")
    first_name = models.CharField(
        max_length=255,
        verbose_name="Имя",
        null=True,
        blank=True
    )
    username = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        unique=True,
        verbose_name="Username"
    )
    contact = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Контакт"
    )
    bot = models.ForeignKey(
        BotInstance,
        on_delete=models.CASCADE,
        verbose_name="Бот",
        null=True,
        blank=True
    )
    is_active = models.BooleanField(
        verbose_name="Активен",
        default=False
    )
    amo_contact_id = models.CharField(
        verbose_name="ID контакта в AmoCRM",
        default=None,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"@{self.username}" if self.username else str(self.telegram_id)

    class Meta:
        verbose_name = "Пользователь Telegram"
        verbose_name_plural = "Пользователи Telegram"


class PDFDocument(models.Model):
    DOCUMENT_TYPES = (
        ('offer', 'Оферта'),
        ('policy', 'Политика'),
        ('personal_data', 'Персональные данные'),
        ('notification', 'Рассылка')
    )

    title = models.CharField(
        "Название",
        max_length=255
    )
    file = models.FileField(
        "PDF файл",
        upload_to='documents/'
    )
    document_type = models.CharField(
        "Тип документа",
        choices=DOCUMENT_TYPES,
        max_length=20
    )
    slug = models.SlugField(
        "Slug",
        unique=True
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.document_type
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return f"https://{Site.objects.get_current().domain}{reverse('view_pdf', args=[str(self.slug)])}"

    class Meta:
        verbose_name = "Документ"
        verbose_name_plural = "Документы"

    def __str__(self):
        return self.title
