from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from CvetoforBots.apps.core.models import BotInstance


TOKEN_MAP = {
    "ULAN_UDE_TOKEN": settings.ULAN_UDE_TOKEN,
    "ANGARSK_TOKEN": settings.ANGARSK_TOKEN,
}


@receiver(post_save, sender=BotInstance)
def replace_bot_instance(sender, instance, created, **kwargs):
    if instance.token in TOKEN_MAP:
        instance.token = TOKEN_MAP[instance.token]
        instance.save()
