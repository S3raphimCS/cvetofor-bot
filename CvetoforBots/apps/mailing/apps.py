from django.apps import AppConfig


class MailingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'CvetoforBots.apps.mailing'
    verbose_name = "Рассылки"
