import os
import subprocess

from django.utils import timezone
from loguru import logger

from CvetoforBots.apps.core.models import BotInstance


class BotService:
    RUNNING = 'running'
    STOPPED = 'stopped'
    COMMAND = ('venv/bin/python3', 'manage.py', 'run_bot')
    # COMMAND = ("python", "manage.py", "run_bot")  # For Windows

    def __init__(self, bot_instance: BotInstance):
        self.bot = bot_instance

    def start(self):
        try:
            if self.bot.status == self.RUNNING:
                return

            process = subprocess.Popen(
                self.COMMAND + (str(self.bot.id),),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            self.update_status(self.RUNNING, process.pid)
        except Exception as err:
            logger.error(f"Ошибка старта бота: {err}")

    def stop(self):
        if self.bot.status != self.RUNNING or not self.bot.pid:
            return

        try:
            os.kill(self.bot.pid, 9)
        except ProcessLookupError as err:
            self.update_status(self.STOPPED, None)
            logger.error(f"Ошибка при остановке бота: {err}")
        except OSError as err:
            self.update_status(self.STOPPED, None)
            logger.error(f"Ошибка при остановке бота: {err}")

        self.update_status(self.STOPPED, None)

    def update_status(self, status, pid):
        try:
            self.bot.status = status
            self.bot.pid = pid

            if self.bot.status == self.RUNNING:
                self.bot.started_at = timezone.now()
            else:
                self.bot.down_at = timezone.now()

            self.bot.save()
        except Exception as err:
            logger.error(f"Ошибка при изменении статуса бота: {err}")
