from typing import Any

from telebot import types

from CvetoforBots.apps.core.keyboards import KeyboardBuilder
from CvetoforBots.apps.core.models import PDFDocument, TelegramUser
from CvetoforBots.common import constants


def start_handler(
        message: types.Message,
        context: dict[str, Any]
):
    bot = context['bot']
    bot_instance = context['bot_instance']

    document_buttons = []

    for btn in [
        constants.DocumentButtons.OFFER,
        constants.DocumentButtons.POLICY,
        constants.DocumentButtons.PERSONAL_DATA,
        constants.DocumentButtons.NOTIFICATION,
    ]:
        doc = PDFDocument.objects.filter(slug=btn.slug).first()
        if doc:
            url = doc.get_absolute_url()
            document_buttons.append(
                types.InlineKeyboardButton(btn.text, web_app=types.WebAppInfo(url=url))
            )

    user = TelegramUser.objects.filter(telegram_id=message.from_user.id).first()
    if not user:
        TelegramUser.objects.create(
            telegram_id=message.from_user.id,
            username="@" + message.from_user.username if message.from_user.username else None,
            bot=bot_instance,
        )

    kb_builder = KeyboardBuilder()

    document_keyboard = kb_builder.add_rows(document_buttons, row_width=1).build()

    bot.send_message(
        chat_id=message.chat.id,
        text=constants.START_TEXT.format(title=bot_instance.title),
        reply_markup=document_keyboard,
        parse_mode="HTML",
    )

    agree_text, agree_callback_data = constants.DocumentButtons.USER_AGREE
    agree_btn = types.InlineKeyboardButton(text=agree_text, callback_data=agree_callback_data)
    agree_keyboard = KeyboardBuilder().add_row(agree_btn).build()

    bot.send_message(
        chat_id=message.chat.id,
        text=constants.AGREEMENT_TEXT,
        reply_markup=agree_keyboard,
        parse_mode="HTML"
    )


def menu_handler(
        message: types.Message,
        context: dict[str, Any]
):
    bot = context['bot']
    kb_builder = KeyboardBuilder()
    categories_buttons = [
        types.InlineKeyboardButton(
            constants.CategoryButtons.BUDGET_BOUQUET.text,
            callback_data=constants.CategoryButtons.BUDGET_BOUQUET.callback
        ),
        types.InlineKeyboardButton(
            constants.CategoryButtons.BY_FLOWER_BOUQUET.text,
            callback_data=constants.CategoryButtons.BY_FLOWER_BOUQUET.callback
        )
    ]

    categories_keyboard = kb_builder.add_rows(categories_buttons, row_width=1).build()

    bot.send_message(
        chat_id=message.chat.id,
        text=constants.CATEGORIES_CHOICE_TEXT,
        reply_markup=categories_keyboard,
        parse_mode="HTML",
    )
