from django.core.management.base import BaseCommand

from CvetoforBots.apps.core.models import BotInstance
from CvetoforBots.apps.core.runner import TelegramBot


class Command(BaseCommand):
    help = "Запускает бота по ID"

    def add_arguments(self, parser):
        parser.add_argument('bot_id', type=int)

    def handle(self, *args, **options):
        bot_id = options['bot_id']
        try:
            bot_instance = BotInstance.objects.get(id=bot_id)
            telegram_bot = TelegramBot(bot_instance)
            telegram_bot.run()
        except BotInstance.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Бот с ID={bot_id} не найден"))
