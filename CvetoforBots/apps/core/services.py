import os
import subprocess

from django.utils import timezone

from CvetoforBots.apps.core.models import BotInstance


class BotService:
    RUNNING = 'running'
    STOPPED = 'stopped'
    COMMAND = ('python', 'manage.py', 'run_bot')

    def __init__(self, bot_instance: BotInstance):
        self.bot = bot_instance

    def start(self):
        if self.bot.status == self.RUNNING:
            return

        process = subprocess.Popen(
            self.COMMAND + (str(self.bot.id),),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        self.update_status(self.RUNNING, process.pid)

    def stop(self):
        if self.bot.status != self.RUNNING or not self.bot.pid:
            return

        try:
            os.kill(self.bot.pid, 9)
        except ProcessLookupError:
            self.update_status(self.STOPPED, None)
        except OSError:
            self.update_status(self.STOPPED, None)


        self.update_status(self.STOPPED, None)

    def update_status(self, status, pid):
        self.bot.status = status
        self.bot.pid = pid

        if self.bot.status == self.RUNNING:
            self.bot.started_at = timezone.now()
        else:
            self.bot.down_at = timezone.now()

        self.bot.save()
