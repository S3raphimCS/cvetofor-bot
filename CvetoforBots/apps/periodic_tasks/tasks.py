from pathlib import Path

from django.contrib.auth import get_user_model
from django.db.models import Count
from django.utils import timezone
from loguru import logger
from telebot import apihelper, types

from CvetoforBots import celery_app
from CvetoforBots.apps.core.keyboards import KeyboardBuilder
from CvetoforBots.apps.core.models import TelegramUser
from CvetoforBots.apps.core.runner import TelegramBot
from CvetoforBots.apps.mailing.enums import RecipientType, SendingStatus
from CvetoforBots.apps.mailing.models import Mailing, MailingLog


User = get_user_model()


@celery_app.app.task
def send_instant_mailing() -> None:
    """Задача отправки рассылки со статусом ready_to_send=True и is_instant=True."""
    mailings = Mailing.objects.filter(ready_to_send=True, is_processed=False, is_instant=True)
    for mailing in mailings:
        bot = TelegramBot(mailing.bot).bot
        match mailing.recipient_type:
            case RecipientType.ALL.value:
                subs = TelegramUser.objects.filter(bot=mailing.bot, is_active=True)

            case RecipientType.NEW.value:
                subs = TelegramUser.objects.annotate(order_count=Count("orders")).filter(order_count=0, bot=mailing.bot,
                                                                                         is_active=True)
            case RecipientType.ONE.value:
                subs = TelegramUser.objects.annotate(order_count=Count("orders")).filter(order_count=1, bot=mailing.bot,
                                                                                         is_active=True)
            case RecipientType.REGULAR.value:
                subs = TelegramUser.objects.annotate(order_count=Count("orders")).filter(order_count__gte=2,
                                                                                         bot=mailing.bot,
                                                                                         is_active=True)
        for sub in subs:
            try:
                keyboard = None
                if mailing.button_link and mailing.button_link:
                    kb_builder = KeyboardBuilder()
                    buttons_list = [
                        types.InlineKeyboardButton(f"{mailing.button_text}",
                                                   callback_data="pay-order", url=mailing.button_link),
                    ]
                    kb_builder.add_rows(buttons_list, row_width=1)
                    keyboard = kb_builder.build()
                if mailing.image:
                    photo = Path(mailing.image.path)
                    bot.send_photo(
                        chat_id=sub.telegram_id,
                        photo=photo.open(mode="rb"),
                        caption=mailing.body,
                        reply_markup=keyboard
                    )
                else:
                    bot.send_message(
                        chat_id=sub.telegram_id,
                        text=mailing.body,
                        reply_markup=keyboard
                    )
            except apihelper.ApiTelegramException as e:
                if e.error_code == 403 and "bot was blocked by the user" in e.description:
                    sub.is_active = False
                    sub.save(update_fields=["is_active"])
                    logger.info(f"Пользователь {sub.telegram_id} заблокировал бота.")
                elif e.error_code == 400 and "chat not found" in e.description:
                    sub.is_active = False
                    sub.save(update_fields=["is_active"])
                    logger.warning(f"Чат {sub.telegram_id} не найден. Деактивируем.")
                else:
                    logger.error(f"Неожиданная ошибка Telegram API для пользователя {sub.telegram_id}: {e}")
                MailingLog.objects.create(mail=mailing, user_id=sub.telegram_id, error=e,
                                          sending_status=SendingStatus.ERROR)
            except Exception as err:
                MailingLog.objects.create(mail=mailing, user_id=sub.telegram_id, error=err,
                                          sending_status=SendingStatus.ERROR)
                logger.error(f"Ошибка при отправке рассылки: {err}")
            else:
                MailingLog.objects.create(mail=mailing, user_id=sub.telegram_id, sending_status=SendingStatus.SUCCESS)
                logger.info("Отправка рассылки успешно завершена")

        mailing.is_processed = True
        mailing.save(update_fields=["is_processed"])


@celery_app.app.task
def send_timed_mailing() -> None:
    """Задача отправки рассылки со статусом ready_to_send=True и is_instant=True."""
    now = timezone.now()
    mailings = Mailing.objects.filter(ready_to_send=True, is_processed=False, is_instant=False, time_start__lte=now)
    for mailing in mailings:
        bot = TelegramBot(mailing.bot).bot
        match mailing.recipient_type:
            case RecipientType.ALL.value:
                subs = TelegramUser.objects.filter(bot=mailing.bot, is_active=True)

            case RecipientType.NEW.value:
                subs = TelegramUser.objects.annotate(order_count=Count("orders")).filter(order_count=0, bot=mailing.bot,
                                                                                         is_active=True)
            case RecipientType.ONE.value:
                subs = TelegramUser.objects.annotate(order_count=Count("orders")).filter(order_count=1, bot=mailing.bot,
                                                                                         is_active=True)
            case RecipientType.REGULAR.value:
                subs = TelegramUser.objects.annotate(order_count=Count("orders")).filter(order_count__gte=2,
                                                                                         bot=mailing.bot,
                                                                                         is_active=True)
        for sub in subs:
            try:
                keyboard = None
                if mailing.button_link and mailing.button_link:
                    kb_builder = KeyboardBuilder()
                    buttons_list = [
                        types.InlineKeyboardButton(f"{mailing.button_text}",
                                                   callback_data="pay-order", url=mailing.button_link),
                    ]
                    kb_builder.add_rows(buttons_list, row_width=1)
                    keyboard = kb_builder.build()
                if mailing.image:
                    photo = Path(mailing.image.path)
                    bot.send_photo(
                        chat_id=sub.telegram_id,
                        photo=photo.open(mode="rb"),
                        caption=mailing.body,
                        reply_markup=keyboard
                    )
                else:
                    bot.send_message(
                        chat_id=sub.telegram_id,
                        text=mailing.body,
                        reply_markup=keyboard
                    )
            except apihelper.ApiTelegramException as e:
                if e.error_code == 403 and "bot was blocked by the user" in e.description:
                    sub.is_active = False
                    sub.save(update_fields=["is_active"])
                    logger.info(f"Пользователь {sub.telegram_id} заблокировал бота.")
                elif e.error_code == 400 and "chat not found" in e.description:
                    sub.is_active = False
                    sub.save(update_fields=["is_active"])
                    logger.warning(f"Чат {sub.telegram_id} не найден. Деактивируем.")
                else:
                    logger.error(f"Неожиданная ошибка Telegram API для пользователя {sub.telegram_id}: {e}")
                MailingLog.objects.create(mail=mailing, user_id=sub.telegram_id, error=e,
                                          sending_status=SendingStatus.ERROR)
            except Exception as err:
                MailingLog.objects.create(mail=mailing, user_id=sub.telegram_id, error=err,
                                          sending_status=SendingStatus.ERROR)
                logger.error(f"Ошибка при отправке рассылки: {err}")
            else:
                MailingLog.objects.create(mail=mailing, user_id=sub.telegram_id, sending_status=SendingStatus.SUCCESS)
                logger.info("Отправка рассылки успешно завершена")

        mailing.is_processed = True
        mailing.save(update_fields=["is_processed"])
