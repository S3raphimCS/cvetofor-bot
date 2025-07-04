import logging

import telebot

from CvetoforBots.apps.core.handlers import callbacks, messages
from CvetoforBots.apps.core.handlers.context_wrapper import (
    with_callback_context,
    with_context,
)
from CvetoforBots.apps.core.models import BotInstance
from CvetoforBots.common import constants
from time import sleep


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


class TelegramBot:
    def __init__(self, bot_instance: BotInstance):
        self.bot_instance = bot_instance
        self.bot = telebot.TeleBot(bot_instance.token)

    def setup_handlers(self):
        callback_handlers_map = {
            callbacks.next_bouquet_callback: {
                'func': lambda callback: callback.data.startswith("next")
            },
            callbacks.edit_message_to_menu: {
                "func": lambda callback: callback.data == "edit_message_to_menu"
            },
            callbacks.menu: {
                "func": lambda callback: callback.data == "menu"
            },
            callbacks.category_callback: {
                'func': lambda callback: callback.data == 'user_agreed'
            },
            callbacks.budget_bouquets_callback: {
                'func': lambda callback: callback.data == 'budget-bouqet'
            },
            callbacks.flower_bouquets_callback: {
                'func': lambda callback: callback.data == "by-flower-bouqet"
            },
            callbacks.order_callback: {
                "func": lambda callback: callback.data.startswith("order")
            },
            callbacks.post_card_callback: {
                "func": lambda callback: callback.data == "post-card-yes"
            },
            callbacks.post_card_cancel_callback: {
                "func": lambda callback: callback.data == "post-card-no"
            },
            callbacks.ask_old_contact_info: {
                "func": lambda callback: callback.data == "ask-old-contact-info"
            },
            callbacks.set_order_old_info_handler: {
                "func": lambda callback: callback.data == "set-old-info"
            },
            callbacks.go_to_new_contact_info: {
                "func": lambda callback: callback.data == "go-to-new-contact-info"
            },
            callbacks.ask_delivery_date: {
                "func": lambda callback: callback.data.startswith("date")
            },
            callbacks.ask_delivery_time: {
                "func": lambda callback: callback.data.startswith("time-interval")
            },
            callbacks.handle_flower_filter: {
                'func': lambda callback: callback.data.startswith("flower_filter:"),
            },
            callbacks.handle_budget_filter: {
                'func': lambda callback: callback.data.startswith(
                    "filter:") or callback.data == constants.ActionButtons.NEW_FILTER.callback,
            },
            callbacks.unknown_command_handler: {
                "func": lambda message: message.text.startswith('')
            },  # TODO Тест
        }
        message_handlers_map = {
            messages.start_handler: {'commands': ['start']},
            messages.menu_handler: {'commands': ['menu']},
        }

        context = {
            'bot': self.bot,
            'bot_instance': self.bot_instance,
        }

        for handler, params in message_handlers_map.items():
            wrapped_handler = with_context(handler, context)
            self.bot.register_message_handler(wrapped_handler, **params)

        for handler, params in callback_handlers_map.items():
            wrapped = with_callback_context(handler, context)
            self.bot.register_callback_query_handler(wrapped, **params)

    def run(self):
        self.setup_handlers()
        while True:
            try:
                self.bot.infinity_polling(logger_level=logging.WARNING)
            except Exception:
                sleep(5)
