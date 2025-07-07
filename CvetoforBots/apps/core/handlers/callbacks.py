from typing import Any

from django.conf import settings
from loguru import logger
from telebot import types
from datetime import datetime
from pathlib import Path

from CvetoforBots.apps.core.cache.manager import RedisCacheManager
from CvetoforBots.apps.core.handlers.helpers import (
    combine_duplicate_items,
    get_formatted_component_string,
    make_bouquet_query,
    to_markdown,
    is_valid_russian_phone,
    get_next_four_days_formatted
)
from CvetoforBots.apps.core.keyboards import KeyboardBuilder
from CvetoforBots.apps.core.models import BotInstance, TelegramUser
from CvetoforBots.apps.core.storage import UserStorage
from CvetoforBots.apps.flowers.models import Blocks, GroupProduct, Mediable
from CvetoforBots.apps.orders.enums import OrderStatus, TimeIntervalEnum
from CvetoforBots.apps.orders.models import Order
from CvetoforBots.apps.transactions.models import Transaction
from CvetoforBots.common import constants
from CvetoforBots.services.payments.payment import PaymentService


def menu(callback: types.CallbackQuery | types.Message, context: dict[str, Any]):
    bot = context['bot']
    kb_builder = KeyboardBuilder()

    if isinstance(callback, types.CallbackQuery):
        chat_id = callback.message.chat.id
    else:
        chat_id = callback.chat.id

    if user := TelegramUser.objects.filter(telegram_id=chat_id).first():
        if not user.is_active:
            user.is_active = True
        if not user.username or "@" not in user.username:
            user.username = "@" + callback.from_user.username if callback.from_user.username else None
        user.save(update_fields=["is_active", "username"])

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
        chat_id=chat_id,
        text=constants.CATEGORIES_CHOICE_TEXT,
        reply_markup=categories_keyboard,
        parse_mode="HTML",
    )


def category_callback(callback: types.CallbackQuery, context: dict[str, Any]):
    bot = context['bot']
    bot_instance = context['bot_instance']

    bot.send_message(
        chat_id=callback.message.chat.id,
        text="Вы согласились",
        parse_mode="HTML",
    )

    if not TelegramUser.objects.filter(telegram_id=callback.from_user.id).exists():
        TelegramUser.objects.create(telegram_id=callback.from_user.id,
                                    username="@" + callback.from_user.username if callback.from_user.username else None,
                                    bot=bot_instance)
    else:
        user = TelegramUser.objects.filter(telegram_id=callback.from_user.id).first()
        user.username = callback.from_user.username
        user.is_active = True
        user.save(update_fields=["is_active", "username"])

    kb_builder = KeyboardBuilder()
    welcome_text = (
        """Привет и добро пожаловать!
Этот бот создан для любителей цветов и красивой жизни!"""
    )

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

    if bot_instance.cover:
        cover_path = bot_instance.cover.path
        with open(cover_path, 'rb') as photo:
            bot.send_photo(
                chat_id=callback.message.chat.id,
                photo=photo,
                caption=welcome_text,
                parse_mode="HTML",
            )
    else:
        bot.send_message(
            chat_id=callback.message.chat.id,
            text=welcome_text,
            parse_mode="HTML",
        )

    bot.send_message(
        chat_id=callback.message.chat.id,
        text=constants.CATEGORIES_CHOICE_TEXT,
        reply_markup=categories_keyboard,
        parse_mode="HTML",
    )


def budget_bouquets_callback(callback: types.CallbackQuery, context: dict[str, Any]):
    bot = context['bot']
    kb_builder = KeyboardBuilder()

    filter_buttons = constants.PriceButtons.all()

    buttons_list = [
        types.InlineKeyboardButton(btn_text, callback_data=f"filter:{btn_text}")
        for btn_text in filter_buttons
    ]
    buttons_list.append(types.InlineKeyboardButton("◀️ Назад", callback_data="edit_message_to_menu"))

    kb_builder.add_rows(buttons_list, row_width=1)

    budget_keyboard = kb_builder.build()

    bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        text=constants.CHOOSE_CATEGORIES,
        reply_markup=budget_keyboard,
    )


def flower_bouquets_callback(callback: types.CallbackQuery, context: dict[str, Any]):
    bot = context['bot']
    kb_builder = KeyboardBuilder()

    filter_buttons = constants.FlowerButtons.all()

    buttons_list = [
        types.InlineKeyboardButton(btn_text, callback_data=f"flower_filter:{btn_text}")
        for btn_text in filter_buttons
    ]
    buttons_list.append(types.InlineKeyboardButton("◀️ Назад", callback_data="edit_message_to_menu"))

    kb_builder.add_rows(buttons_list, row_width=1)

    flower_keyboard = kb_builder.build()

    bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        text=constants.CHOOSE_CATEGORIES,
        reply_markup=flower_keyboard,
    )


def edit_message_to_menu(callback: types.CallbackQuery, context: dict[str, Any]):
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
    keyboard = kb_builder.add_rows(categories_buttons, row_width=1).build()

    bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        text=constants.CATEGORIES_CHOICE_TEXT,
        reply_markup=keyboard,
    )


def handle_flower_filter(callback: types.CallbackQuery, context: dict[str, Any]):
    bot = context['bot']
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id
    storage = UserStorage()
    RedisCacheManager.set(
        callback.from_user.id,
        **{"previous_bouquets": []}
    )

    # Получаем или создаём состояние
    current_state = storage.get_current_state(chat_id)
    if current_state is None:
        current_state = {
            'handler': 'flower_filter',
            'filters': set(storage.get_user_filters(chat_id))
        }
        storage.push_state(chat_id, current_state)
    elif current_state.get('handler') != 'flower_filter':
        current_state.update({
            'handler': 'flower_filter',
            'filters': set(storage.get_user_filters(chat_id))
        })

    filter_name = callback.data.split("flower_filter:")[1]
    current_filters = storage.get_user_filters(chat_id)

    if filter_name in current_filters:
        storage.remove_filter(chat_id, filter_name)
        current_state['filters'].discard(filter_name)
    else:
        storage.add_filter(chat_id, filter_name)
        current_state['filters'].add(filter_name)

    current_filters = current_state['filters']
    keyboard = _generate_keyboard(current_filters, flowers=True)

    filters_list = "\n".join(f"✅ {f}" for f in sorted(current_filters))
    text = constants.CHOOSE_CATEGORIES + constants.SELECTED_FILTERS_TEMPLATE.format(filters=filters_list)

    bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=text,
        reply_markup=keyboard
    )

    # Подбор товара под фильтр
    current_filter = list(current_filters)[0]
    flower_filter = make_bouquet_query(current_filter)

    # Букет с кнопкой далее
    bouquet = GroupProduct.objects.prefetch_related("prices").filter(
        flower_filter, deleted_at__isnull=True, remains__market_id=1, remains__published=True,
        prices__market__city__id=98, prices__price__isnull=False, prices__deleted_at__isnull=True).order_by(
        "prices__price").first()
    if bouquet:
        compound = Blocks.objects.filter(blockable_type="App\Models\GroupProduct").filter(  # noqa
            blockable_id=bouquet.id).all().order_by("position")
        compound = '\n' + '\n'.join(
            [i for i in [get_formatted_component_string(i.content) for i in compound] if
             i is not None]) if compound.exists() else None
        if compound:
            compound = combine_duplicate_items(compound)
        bouquet_text = (
            f"{bouquet.title} за {bouquet.prices.filter(price__isnull=False, deleted_at__isnull=True, market__city__id=98).first().price} руб.\n"
            f"{'Описание: ' + bouquet.description if bouquet.description else ''}\n"
            f"{'Состав:' + compound if compound else ''}")
        bouquet_text = to_markdown(bouquet_text)
        # Клавиатура
        kb_builder = KeyboardBuilder()
        buttons_list = [
            types.InlineKeyboardButton(constants.NavButtons.NEXT.text,
                                       callback_data=constants.NavButtons.NEXT.callback + f" {bouquet.id} flower_filter:{current_filter}"),
            types.InlineKeyboardButton(constants.ActionButtons.CHOOSE.text,
                                       callback_data=constants.ActionButtons.CHOOSE.callback + f" {bouquet.id}"),
            types.InlineKeyboardButton("🏠 В меню", callback_data="menu")
        ]
        kb_builder.add_rows(buttons_list, row_width=1)
        keyboard = kb_builder.build()

        bouquet_photo_path = Mediable.objects.filter(
            mediable_type="App\Models\GroupProduct",
            deleted_at=None,
            mediable_id=bouquet.id)[1]
        if hasattr(bouquet_photo_path, "media"):
            if bouquet_photo_path.media.uuid:
                photo_path = Path(settings.PATH_TO_MEDIA_ON_SERVER + "/" + bouquet_photo_path.media.uuid)
                if photo_path.exists():
                    if len(bouquet_text) > 1024:
                        bouquet_text = (
                            f"{bouquet.title} за {bouquet.prices.filter(price__isnull=False, deleted_at__isnull=True, market__city__id=98).first().price} руб.\n"
                            f"{'Состав:' + compound if compound else ''}")
                    return bot.send_photo(
                        chat_id=chat_id,
                        caption=bouquet_text,
                        reply_markup=keyboard,
                        photo=photo_path.open(mode="rb"),
                        parse_mode="markdown"
                    )
        bot.send_message(
            chat_id=chat_id,
            text=bouquet_text,
            reply_markup=keyboard,
            parse_mode="markdown"
        )
    else:
        kb_builder = KeyboardBuilder()
        buttons_list = [
            types.InlineKeyboardButton("Вернуться к выбору букета", callback_data="menu")
        ]
        kb_builder.add_rows(buttons_list, row_width=1)
        keyboard = kb_builder.build()
        bot.send_message(
            chat_id=chat_id,
            text="Букетов с выбранным фильтром не найдено",
            reply_markup=keyboard,
            parse_mode="HTML"
        )


def handle_budget_filter(callback: types.CallbackQuery, context: dict[str, Any]):
    bot = context['bot']
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id
    storage = UserStorage()
    RedisCacheManager.set(
        callback.from_user.id,
        **{"previous_bouquets": []}
    )

    # Получаем или создаём состояние
    current_state = storage.get_current_state(chat_id)
    if current_state is None:
        current_state = {
            'handler': 'filter',
            'filters': set(storage.get_user_filters(chat_id))
        }
        storage.push_state(chat_id, current_state)
    elif current_state.get('handler') != 'filter':
        current_state.update({
            'handler': 'filter',
            'filters': set(storage.get_user_filters(chat_id))
        })

    filter_name = callback.data.split("filter:")[1]
    current_filters = storage.get_user_filters(chat_id)

    if filter_name in current_filters:
        storage.remove_filter(chat_id, filter_name)
        current_state['filters'].discard(filter_name)
    else:
        storage.add_filter(chat_id, filter_name)
        current_state['filters'].add(filter_name)

    current_filters = current_state['filters']
    keyboard = _generate_keyboard(current_filters, flowers=False)

    filters_list = "\n".join(f"✅ {f}" for f in sorted(current_filters))
    text = constants.CHOOSE_CATEGORIES + constants.SELECTED_FILTERS_TEMPLATE.format(filters=filters_list)

    bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=text,
        reply_markup=keyboard
    )

    # Подбор товара под фильтр
    current_filter = list(current_filters)[0]
    price_filter = make_bouquet_query(current_filter)

    # Букет с кнопкой далее
    bouquet = GroupProduct.objects.prefetch_related("prices").filter(
        price_filter, deleted_at__isnull=True, remains__market_id=1, remains__published=True, title__icontains="букет",
        prices__market__city__id=98, prices__price__isnull=False, prices__deleted_at__isnull=True).order_by(
        "prices__price").first()
    if bouquet:
        compound = Blocks.objects.filter(blockable_type="App\Models\GroupProduct").filter(  # noqa
            blockable_id=bouquet.id).all().order_by("position")
        compound = '\n' + '\n'.join(
            [i for i in [get_formatted_component_string(i.content) for i in compound] if
             i is not None]) if compound.exists() else None
        if compound:
            compound = combine_duplicate_items(compound)
        bouquet_text = (
            f"{bouquet.title} за {bouquet.prices.filter(price__isnull=False, deleted_at__isnull=True, market__city__id=98).first().price} руб.\n"
            f"{'Описание: ' + bouquet.description if bouquet.description else ''}\n"
            f"{'Состав:' + compound if compound else ''}")
        bouquet_text = to_markdown(bouquet_text)
        # Клавиатура
        kb_builder = KeyboardBuilder()
        buttons_list = [
            types.InlineKeyboardButton(constants.NavButtons.NEXT.text,
                                       callback_data=constants.NavButtons.NEXT.callback + f" {bouquet.id} filter:{current_filter}"),
            types.InlineKeyboardButton(constants.ActionButtons.CHOOSE.text,
                                       callback_data=constants.ActionButtons.CHOOSE.callback + f" {bouquet.id}"),
            types.InlineKeyboardButton("🏠 В меню", callback_data="menu")
        ]
        kb_builder.add_rows(buttons_list, row_width=1)
        keyboard = kb_builder.build()

        bouquet_photo_path = Mediable.objects.filter(
            mediable_type="App\Models\GroupProduct",
            deleted_at=None,
            mediable_id=bouquet.id)[1]
        if hasattr(bouquet_photo_path, "media"):
            if bouquet_photo_path.media.uuid:
                photo_path = Path(settings.PATH_TO_MEDIA_ON_SERVER + "/" + bouquet_photo_path.media.uuid)
                if photo_path.exists():
                    if len(bouquet_text) > 1024:
                        bouquet_text = (
                            f"{bouquet.title} за {bouquet.prices.filter(price__isnull=False, deleted_at__isnull=True, market__city__id=98).first().price} руб.\n"
                            f"{'Состав:' + compound if compound else ''}")
                    return bot.send_photo(
                        chat_id=chat_id,
                        caption=bouquet_text,
                        reply_markup=keyboard,
                        photo=photo_path.open(mode="rb"),
                        parse_mode="markdown"
                    )

        bot.send_message(
            chat_id=chat_id,
            text=bouquet_text,
            reply_markup=keyboard,
            parse_mode="markdown"
        )
    else:
        kb_builder = KeyboardBuilder()
        buttons_list = [
            types.InlineKeyboardButton("Вернуться к выбору букета", callback_data="menu")
        ]
        kb_builder.add_rows(buttons_list, row_width=1)
        keyboard = kb_builder.build()
        bot.send_message(
            chat_id=chat_id,
            text="Букетов с выбранным фильтром не найдено",
            reply_markup=keyboard,
            parse_mode="HTML"
        )


def next_bouquet_callback(callback: types.CallbackQuery, context: dict[str, Any]):
    bot = context['bot']
    chat_id = callback.message.chat.id
    bouquet_id = callback.data.split()[1]

    user_data = RedisCacheManager.get(callback.from_user.id)
    prev_bouquets = user_data.get("previous_bouquets", [])
    prev_bouquets.append(bouquet_id)
    user_data["previous_bouquets"] = prev_bouquets
    RedisCacheManager.set(callback.from_user.id, **user_data)

    if "flower_filter" in callback.data:
        query_filter = make_bouquet_query(callback.data.split("flower_filter:")[1])
        next_bouquet = GroupProduct.objects.prefetch_related("prices").exclude(id__in=prev_bouquets).filter(
            query_filter, deleted_at__isnull=True, remains__market_id=1, remains__published=True,
            prices__price__gte=GroupProduct.objects.prefetch_related("prices").get(id=bouquet_id).prices.filter(
                price__isnull=False, deleted_at__isnull=True, market__city__id=98).first().price,
            prices__market__city__id=98, prices__price__isnull=False, prices__deleted_at__isnull=True).order_by(
            "prices__price").first()
    else:
        query_filter = make_bouquet_query(callback.data.split("filter:")[1])
        next_bouquet = GroupProduct.objects.prefetch_related("prices").exclude(id__in=prev_bouquets).filter(
            query_filter, deleted_at__isnull=True, remains__market_id=1, remains__published=True,
            title__icontains="букет",
            prices__price__gte=GroupProduct.objects.prefetch_related("prices").get(id=bouquet_id).prices.filter(
                price__isnull=False, deleted_at__isnull=True, market__city__id=98).first().price,
            prices__market__city__id=98, prices__price__isnull=False, prices__deleted_at__isnull=True).order_by(
            "prices__price").first()
    kb_builder = KeyboardBuilder()
    if next_bouquet:
        if "flower_filter" in callback.data:
            buttons_list = [
                types.InlineKeyboardButton(constants.NavButtons.NEXT.text,
                                           callback_data=constants.NavButtons.NEXT.callback + f" {next_bouquet.id} flower_filter:{callback.data.split('flower_filter:')[1]}"),
                types.InlineKeyboardButton(constants.ActionButtons.CHOOSE.text,
                                           callback_data=constants.ActionButtons.CHOOSE.callback + f" {next_bouquet.id}"),
                types.InlineKeyboardButton("🏠 В меню", callback_data="menu")
            ]
        else:
            buttons_list = [
                types.InlineKeyboardButton(constants.NavButtons.NEXT.text,
                                           callback_data=constants.NavButtons.NEXT.callback + f" {next_bouquet.id} filter:{callback.data.split('filter:')[1]}"),
                types.InlineKeyboardButton(constants.ActionButtons.CHOOSE.text,
                                           callback_data=constants.ActionButtons.CHOOSE.callback + f" {next_bouquet.id}"),
                types.InlineKeyboardButton("🏠 В меню", callback_data="menu")
            ]
        kb_builder.add_rows(buttons_list, row_width=1)
        keyboard = kb_builder.build()
        compound = Blocks.objects.filter(blockable_type="App\Models\GroupProduct").filter(  # noqa
            blockable_id=next_bouquet.id).all().order_by("position")
        compound = '\n' + '\n'.join(
            [i for i in [get_formatted_component_string(i.content) for i in compound] if
             i is not None]) if compound.exists() else None
        if compound:
            compound = combine_duplicate_items(compound)
        bouquet_text = (
            f"{next_bouquet.title} за {next_bouquet.prices.filter(price__isnull=False, deleted_at__isnull=True, market__city__id=98).first().price} руб.\n"
            f"{'Описание: ' + next_bouquet.description if next_bouquet.description else ''}\n"
            f"{'Состав:' + compound if compound else ''}")
        bouquet_text = to_markdown(bouquet_text)
        bouquet_photo_path = Mediable.objects.filter(
            mediable_type="App\Models\GroupProduct",
            deleted_at=None,
            mediable_id=next_bouquet.id)[1]
        if hasattr(bouquet_photo_path, "media"):
            if bouquet_photo_path.media.uuid:
                photo_path = Path(settings.PATH_TO_MEDIA_ON_SERVER + "/" + bouquet_photo_path.media.uuid)
                if photo_path.exists():
                    if len(bouquet_text) > 1024:
                        bouquet_text = (
                            f"{next_bouquet.title} за {next_bouquet.prices.filter(price__isnull=False, deleted_at__isnull=True, market__city__id=98).first().price} руб.\n"
                            f"{'Состав:' + compound if compound else ''}")
                    return bot.send_photo(
                        chat_id=chat_id,
                        caption=bouquet_text,
                        reply_markup=keyboard,
                        photo=photo_path.open(mode="rb"),
                        parse_mode="markdown"
                    )
        bot.send_message(
            chat_id=chat_id,
            text=bouquet_text,
            reply_markup=keyboard,
            parse_mode="markdown"
        )
    else:
        buttons_list = [
            types.InlineKeyboardButton("Вернуться к выбору букета", callback_data="menu")
        ]
        kb_builder.add_rows(buttons_list, row_width=1)
        keyboard = kb_builder.build()
        bot.send_message(
            chat_id=chat_id,
            text="Это был последний букет",
            reply_markup=keyboard
        )


def order_callback(callback: types.CallbackQuery, context: dict[str, Any]):
    bot = context['bot']
    chat_id = callback.message.chat.id
    product_id = callback.data.split()[1]
    product = GroupProduct.objects.prefetch_related("prices").get(id=product_id)
    RedisCacheManager.set(
        callback.from_user.id,
        **{
            "group_product_id": product_id,
            "post_card": False,
            "post_card_text": None,
            "user_name": None,
            "user_contact": None,
            "recipient_name": None,
            "recipient_phone": None,
            "recipient_address": None,
            "delivery_date": None,
            "time_interval": None,
            "amount": float(
                product.prices.filter(price__isnull=False, deleted_at__isnull=True, market__city__id=98).first().price),
        }
    )
    kb_builder = KeyboardBuilder()
    buttons_list = [
        types.InlineKeyboardButton(constants.PostCardButtons.YES.text,
                                   callback_data=constants.PostCardButtons.YES.callback),
        types.InlineKeyboardButton(constants.PostCardButtons.NO.text,
                                   callback_data="ask-old-contact-info")
    ]
    kb_builder.add_rows(buttons_list, row_width=2)
    keyboard = kb_builder.build()
    bot.send_message(
        chat_id=chat_id,
        text="Для выхода с любого этапе оформления заказа напишите /menu.\nХотите ли вы добавить открытку к букету?",
        reply_markup=keyboard
    )


def post_card_callback(callback: types.CallbackQuery, context: dict[str, Any]):
    bot = context['bot']
    chat_id = callback.message.chat.id
    bot.send_message(
        chat_id=chat_id,
        text="Введите текст для открытки, не более 120 слов",
    )
    bot.register_next_step_handler_by_chat_id(callback.message.chat.id, ask_post_card_text, context)


def ask_old_contact_info(callback: types.CallbackQuery | types.Message, context: dict[str, Any]):
    bot = context['bot']
    if isinstance(callback, types.CallbackQuery):
        chat_id = callback.message.chat.id
    else:
        chat_id = callback.chat.id
    tg_user = TelegramUser.objects.filter(telegram_id=callback.from_user.id).first()
    if hasattr(tg_user, "first_name") and hasattr(tg_user, "contact"):
        if tg_user.first_name and tg_user.contact:
            user_name, user_contact = tg_user.first_name, tg_user.contact
            kb_builder = KeyboardBuilder()
            message = f"Ваше имя '{user_name}' и контактные данные '{user_contact}'?"
            buttons_list = [
                types.InlineKeyboardButton(constants.PostCardButtons.YES.text,
                                           callback_data="set-old-info"),
                types.InlineKeyboardButton(constants.PostCardButtons.NO.text,
                                           callback_data="go-to-new-contact-info")
            ]
            kb_builder.add_rows(buttons_list, row_width=2)
            keyboard = kb_builder.build()
            bot.send_message(
                chat_id=chat_id,
                text=message,
                reply_markup=keyboard,
            )
        else:
            bot.send_message(
                chat_id=chat_id,
                text="Введите ваше имя"
            )
            bot.register_next_step_handler_by_chat_id(callback.message.chat.id, ask_customer_name, context)
    else:
        bot.send_message(
            chat_id=chat_id,
            text="Введите ваше имя"
        )
        bot.register_next_step_handler_by_chat_id(callback.message.chat.id, ask_customer_name, context)


def set_order_old_info_handler(callback: types.CallbackQuery, context: dict[str, Any]):
    bot = context['bot']
    chat_id = callback.message.chat.id
    order_details = RedisCacheManager.get(callback.from_user.id)
    user = TelegramUser.objects.get(telegram_id=callback.from_user.id)
    order_details["user_name"] = user.first_name
    order_details["user_contact"] = user.contact
    RedisCacheManager.set(callback.from_user.id, **order_details)
    bot.send_message(
        chat_id=chat_id,
        text="Введите имя получателя"
    )
    bot.register_next_step_handler_by_chat_id(chat_id, ask_recipient_name, context)


def go_to_new_contact_info(callback: types.CallbackQuery, context: dict[str, Any]):
    bot = context['bot']
    chat_id = callback.message.chat.id
    bot.send_message(
        chat_id=chat_id,
        text="Введите ваше имя"
    )
    bot.register_next_step_handler_by_chat_id(callback.message.chat.id, ask_customer_name, context)


def post_card_cancel_callback(callback: types.CallbackQuery, context: dict[str, Any]):
    bot = context['bot']
    chat_id = callback.message.chat.id
    bot.send_message(
        chat_id=chat_id,
        text="Введите ваше имя"
    )
    bot.register_next_step_handler_by_chat_id(callback.message.chat.id, ask_customer_name, context)


def ask_post_card_text(message, context: dict[str, Any]):
    bot = context['bot']
    chat_id = message.chat.id
    try:
        if message.text != "/menu":
            post_card_text = message.text
            order_details = RedisCacheManager.get(message.from_user.id)
            order_details["post_card"] = True
            order_details["post_card_text"] = post_card_text
            RedisCacheManager.set(message.from_user.id, **order_details)
            ask_old_contact_info(message, context)
        else:
            return menu(message, context)
    except Exception as err:
        logger.error(f"Произошла ошибка: {err}")
        kb_builder = KeyboardBuilder()
        buttons_list = [
            types.InlineKeyboardButton("🏠 Меню",
                                       callback_data="menu"),
        ]
        kb_builder.add_rows(buttons_list, row_width=1)
        keyboard = kb_builder.build()
        bot.send_message(
            chat_id=chat_id,
            text="Что-то пошло не так",
            reply_markup=keyboard
        )


def ask_customer_name(message, context: dict[str, Any]):
    bot = context['bot']
    chat_id = message.chat.id
    try:
        if message.text != "/menu":
            order_details = RedisCacheManager.get(message.from_user.id)
            order_details["user_name"] = message.text
            RedisCacheManager.set(message.from_user.id, **order_details)
            bot.send_message(
                chat_id=chat_id,
                text="Введите ваш номер телефона в формате 79123456789"
            )
            bot.register_next_step_handler_by_chat_id(message.chat.id, ask_customer_contact, context)
        else:
            return menu(message, context)
    except Exception as err:
        logger.error(f"Произошла ошибка: {err}")
        kb_builder = KeyboardBuilder()
        buttons_list = [
            types.InlineKeyboardButton("🏠 Меню",
                                       callback_data="menu"),
        ]
        kb_builder.add_rows(buttons_list, row_width=1)
        keyboard = kb_builder.build()
        bot.send_message(
            chat_id=chat_id,
            text="Что-то пошло не так",
            reply_markup=keyboard
        )


def ask_customer_contact(message, context: dict[str, Any]):
    bot = context['bot']
    chat_id = message.chat.id
    try:
        if message.text != "/menu":
            if not is_valid_russian_phone(message.text):
                bot.send_message(
                    chat_id=chat_id,
                    text="Некорректно введенный номер. Попробуйте еще раз"
                )
                bot.register_next_step_handler_by_chat_id(message.chat.id, ask_customer_contact, context)
            else:
                order_details = RedisCacheManager.get(message.from_user.id)
                order_details["user_contact"] = message.text
                RedisCacheManager.set(message.from_user.id, **order_details)
                bot.send_message(
                    chat_id=chat_id,
                    text="Введите имя получателя"
                )
                bot.register_next_step_handler_by_chat_id(message.chat.id, ask_recipient_name, context)
        else:
            return menu(message, context)
    except Exception as err:
        logger.error(f"Произошла ошибка: {err}")
        kb_builder = KeyboardBuilder()
        buttons_list = [
            types.InlineKeyboardButton("🏠 Меню",
                                       callback_data="menu"),
        ]
        kb_builder.add_rows(buttons_list, row_width=1)
        keyboard = kb_builder.build()
        bot.send_message(
            chat_id=chat_id,
            text="Что-то пошло не так",
            reply_markup=keyboard
        )


def ask_recipient_name(message, context: dict[str, Any]):
    bot = context['bot']
    chat_id = message.chat.id
    try:
        if message.text != "/menu":
            order_details = RedisCacheManager.get(message.from_user.id)
            order_details["recipient_name"] = message.text
            RedisCacheManager.set(message.from_user.id, **order_details)
            bot.send_message(
                chat_id=chat_id,
                text="Введите телефон получателя (в формате 79123456789)"
            )
            bot.register_next_step_handler_by_chat_id(message.chat.id, ask_recipient_phone, context)
        else:
            return menu(message, context)
    except Exception as err:
        logger.error(f"Произошла ошибка: {err}")
        kb_builder = KeyboardBuilder()
        buttons_list = [
            types.InlineKeyboardButton("🏠 Меню",
                                       callback_data="menu"),
        ]
        kb_builder.add_rows(buttons_list, row_width=1)
        keyboard = kb_builder.build()
        bot.send_message(
            chat_id=chat_id,
            text="Что-то пошло не так",
            reply_markup=keyboard
        )


def ask_recipient_phone(message, context: dict[str, Any]):
    bot = context['bot']
    chat_id = message.chat.id
    try:
        if message.text != "/menu":
            if not is_valid_russian_phone(message.text):
                bot.send_message(
                    chat_id=chat_id,
                    text="Некорректно введенный номер. Попробуйте еще раз"
                )
                bot.register_next_step_handler_by_chat_id(message.chat.id, ask_recipient_phone, context)
            else:
                order_details = RedisCacheManager.get(message.from_user.id)
                order_details["recipient_phone"] = message.text
                RedisCacheManager.set(message.from_user.id, **order_details)
                kb_builder = KeyboardBuilder()
                dates = get_next_four_days_formatted()
                buttons_list = [types.InlineKeyboardButton(date, callback_data=f"date {date}") for date in dates]
                kb_builder.add_rows(buttons_list, row_width=2)
                keyboard = kb_builder.build()
                bot.send_message(
                    chat_id=chat_id,
                    text="Выберите дату для доставки",
                    reply_markup=keyboard
                )
        else:
            return menu(message, context)
    except Exception as err:
        logger.error(f"Произошла ошибка: {err}")
        kb_builder = KeyboardBuilder()
        buttons_list = [
            types.InlineKeyboardButton("🏠 Меню",
                                       callback_data="menu"),
        ]
        kb_builder.add_rows(buttons_list, row_width=1)
        keyboard = kb_builder.build()
        bot.send_message(
            chat_id=chat_id,
            text="Что-то пошло не так",
            reply_markup=keyboard
        )


def ask_delivery_date(callback: types.CallbackQuery, context: dict[str, Any]):
    bot = context['bot']
    chat_id = callback.message.chat.id
    date = callback.data.split()[1]
    try:
        order_details = RedisCacheManager.get(callback.message.from_user.id)
        order_details["delivery_date"] = date
        RedisCacheManager.set(callback.message.chat.id, **order_details)
        kb_builder = KeyboardBuilder()
        buttons_list = [types.InlineKeyboardButton(i, callback_data=f"time-interval {i}") for i in
                        TimeIntervalEnum.values]
        kb_builder.add_rows(buttons_list, row_width=2)
        keyboard = kb_builder.build()
        bot.send_message(
            chat_id=chat_id,
            text="Выберите интервал времени для доставки",
            reply_markup=keyboard
        )
    except Exception as err:
        logger.error(f"Произошла ошибка: {err}")
        kb_builder = KeyboardBuilder()
        buttons_list = [
            types.InlineKeyboardButton("🏠 Меню",
                                       callback_data="menu"),
        ]
        kb_builder.add_rows(buttons_list, row_width=1)
        keyboard = kb_builder.build()
        bot.send_message(
            chat_id=chat_id,
            text="Что-то пошло не так",
            reply_markup=keyboard
        )


def ask_delivery_time(callback: types.CallbackQuery, context: dict[str, Any]):
    bot = context['bot']
    chat_id = callback.message.chat.id
    time_interval = callback.data.split()[1]
    try:
        order_details = RedisCacheManager.get(callback.message.chat.id)
        order_details["time_interval"] = time_interval
        RedisCacheManager.set(callback.message.from_user.id, **order_details)
        bot.send_message(
            chat_id=chat_id,
            text="Введите адрес получателя"
        )
        bot.register_next_step_handler_by_chat_id(callback.message.chat.id, make_order, context)
    except Exception as err:
        logger.error(f"Произошла ошибка: {err}")
        kb_builder = KeyboardBuilder()
        buttons_list = [
            types.InlineKeyboardButton("🏠 Меню",
                                       callback_data="menu"),
        ]
        kb_builder.add_rows(buttons_list, row_width=1)
        keyboard = kb_builder.build()
        bot.send_message(
            chat_id=chat_id,
            text="Что-то пошло не так",
            reply_markup=keyboard
        )


def make_order(message, context: dict[str, Any]):
    bot = context['bot']
    bot_instance = context["bot_instance"]
    chat_id = message.chat.id
    try:
        if message.text != "/menu":
            order_details = RedisCacheManager.get(message.from_user.id)
            order_details["recipient_address"] = message.text
            RedisCacheManager.set(message.from_user.id, **order_details)
            order_price = float(order_details['amount']) + 50 if order_details["post_card"] else order_details['amount']
            message_to_user = (f"Ваш заказ: {GroupProduct.objects.get(id=order_details['group_product_id']).title}"
                               f"{', открытка' if order_details['post_card'] else ''}. "
                               f"Стоимость: {order_details['amount']} руб.")

            user = TelegramUser.objects.filter(telegram_id=chat_id).first()
            compound = Blocks.objects.filter(blockable_type="App\Models\GroupProduct").filter(  # noqa
                blockable_id=order_details["group_product_id"]).all().order_by("position")
            compound = '\n'.join(
                [i for i in [get_formatted_component_string(i.content) for i in compound] if
                 i is not None]) if compound.exists() else None
            if compound:
                compound = combine_duplicate_items(compound)
            order = Order.objects.create(
                telegram_user=user,
                user_name=order_details['user_name'],
                user_contact=order_details['user_contact'],
                recipient_name=order_details['recipient_name'],
                recipient_phone=order_details['recipient_phone'],
                recipient_address=order_details['recipient_address'],
                with_post_card=order_details['post_card'],
                post_card_text=order_details['post_card_text'] if order_details['post_card'] else None,
                bot_instance=bot_instance,
                amount=order_price,
                status=OrderStatus.NEW,
                group_product_id=order_details["group_product_id"],
                compound=compound,
                delivery_date=datetime.strptime(order_details["delivery_date"], '%d.%m.%Y'),
                time_interval=order_details["time_interval"]
            )
            user.contact = order_details['user_contact']
            user.first_name = order_details['user_name']
            user.save(update_fields=['first_name', 'contact'])
            description = f'Оплата заказа \"{order.id}\"'
            payment = Transaction.objects.create(
                user=user,
                order=order,
                amount=order_price,
                description=description,
            )
            redirect_url = settings.YOOKASSA_PAYMENT_ANGARSK_REDIRECT_URL if bot_instance == BotInstance.objects.filter(
                title__icontains="ангарск").first() else settings.YOOKASSA_PAYMENT_ULAN_UDE_REDIRECT_URL
            url = PaymentService(payment, redirect_url).execute()
            kb_builder = KeyboardBuilder()
            buttons_list = [
                types.InlineKeyboardButton("Оплатить",
                                           callback_data="pay-order", url=url),
                types.InlineKeyboardButton("Выйти в меню",
                                           callback_data="menu")
            ]
            kb_builder.add_rows(buttons_list, row_width=1)
            keyboard = kb_builder.build()
            bot.send_message(
                chat_id=chat_id,
                text=message_to_user,
                reply_markup=keyboard
            )
        else:
            return menu(message, context)
    except Exception as err:
        logger.error(f"Произошла ошибка: {err}")
        kb_builder = KeyboardBuilder()
        buttons_list = [
            types.InlineKeyboardButton("🏠 Меню",
                                       callback_data="menu"),
        ]
        kb_builder.add_rows(buttons_list, row_width=1)
        keyboard = kb_builder.build()
        bot.send_message(
            chat_id=chat_id,
            text="Что-то пошло не так",
            reply_markup=keyboard
        )


def unknown_command_handler(message, context: dict[str, Any]):
    bot = context['bot']
    chat_id = message.chat.id
    kb_builder = KeyboardBuilder()
    buttons_list = [
        types.InlineKeyboardButton("🏠 Вернуться в меню",
                                   callback_data="menu"),
    ]
    kb_builder.add_rows(buttons_list, row_width=1)
    keyboard = kb_builder.build()
    bot.send_message(
        chat_id=chat_id,
        text="Введена неизвестная команда",
        reply_markup=keyboard
    )


def _generate_keyboard(filters, flowers=False):
    kb_builder = KeyboardBuilder()

    if flowers:
        filter_buttons = constants.FlowerButtons.all()
    else:
        filter_buttons = constants.PriceButtons.all()

    buttons_list = []
    if flowers:
        for btn_text in filter_buttons:
            label = f"✅ {btn_text}" if btn_text in filters else btn_text
            callback_data = f"flower_filter:{btn_text}"
            buttons_list.append(
                types.InlineKeyboardButton(label, callback_data=callback_data)
            )
    else:
        for btn_text in filter_buttons:
            label = f"✅ {btn_text}" if btn_text in filters else btn_text
            callback_data = f"filter:{btn_text}"
            buttons_list.append(
                types.InlineKeyboardButton(label, callback_data=callback_data)
            )

    kb_builder.add_rows(buttons_list, row_width=1)
    return kb_builder.build()
