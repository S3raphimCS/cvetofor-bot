from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'CvetoforBots.apps.core'
    verbose_name = 'Основное'

    def ready(self):
        import CvetoforBots.apps.core.signals  # noqa
