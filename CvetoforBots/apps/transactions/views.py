import json

from django.conf import settings
from loguru import logger
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from telebot import types
from yookassa.domain.notification import WebhookNotification

from CvetoforBots.apps.core.keyboards import KeyboardBuilder
from CvetoforBots.apps.core.models import BotInstance
from CvetoforBots.apps.core.runner import TelegramBot
from CvetoforBots.apps.flowers.models import GroupProduct
from CvetoforBots.apps.orders.enums import OrderStatus
from CvetoforBots.apps.transactions.enums import PaymentStatus
from CvetoforBots.apps.transactions.models import Transaction
from CvetoforBots.services.amo_crm.service import AmoCRMWrapper


class YookassaWebHookView(APIView):
    """Класс-вью обработки вебхука от ЮКасса."""

    def post(self, request, *args, **kwargs):
        """Принимает хук запросы."""
        json_string = request.body.decode('utf-8')
        data = json.loads(json_string)

        try:
            notification_object = WebhookNotification(data)
            payment = notification_object.object

            if notification_object.event == 'payment.succeeded':
                obj = Transaction.objects.filter(payment_id=payment.id, status=PaymentStatus.NEW.value).first()
                if obj:
                    obj.status = PaymentStatus.SUCCESS
                    obj.error_description = None
                    obj.save(update_fields=['status', 'error_description'])
                    order = Transaction.objects.filter(payment_id=payment.id).first().order
                    order.status = OrderStatus.PAID.value
                    order.save(update_fields=['status'])
                    if order.bot_instance == BotInstance.objects.filter(title__icontains="Ангарск").first():
                        bot_instance = BotInstance.objects.filter(title__icontains="Ангарск").first()
                        bot = TelegramBot(bot_instance).bot
                        group_id = settings.ANGARSK_GROUP_ID
                        message_to_managers = f"""
Новый заказ
Имя заказчика: {order.user_name}
Пользователь: @{order.telegram_user.username}
Состав заказа: {GroupProduct.objects.get(id=order.group_product_id).title}{", открытка" if order.with_post_card else ''}
{'Текст открытки: ' + order.post_card_text if order.with_post_card else ''}
{"Состав букета:" + order.compound if order.compound else ''}
Дата доставки: {order.delivery_date}
Время доставки: {order.time_interval}
                        """
                        bot.send_message(
                            chat_id=group_id,
                            text=message_to_managers,
                            parse_mode="HTML"
                        )
                    else:
                        bot_instance = BotInstance.objects.filter(title__icontains="улан").first()
                        bot = TelegramBot(bot_instance).bot
                        order = Transaction.objects.filter(payment_id=payment.id).first().order
                        amo_crm_lead_id, contact_id = AmoCRMWrapper().create_lead(
                            order.user_name,
                            order.user_contact,
                            int(order.amount),
                            order.telegram_user.username,
                            order.telegram_user.telegram_id,
                            order.recipient_name,
                            order.recipient_phone,
                            order.recipient_address,
                            f"{GroupProduct.objects.get(id=order.group_product_id).title}{', открытка' if order.with_post_card else ''}",
                            order.compound if order.compound else '',
                            order.delivery_date,
                            order.time_interval,
                            post_card_text=f"Текст открытки: {order.post_card_text}" if order.post_card_text else None,
                            contact=int(order.telegram_user.amo_contact_id) if order.telegram_user.amo_contact_id else None
                        )
                        if amo_crm_lead_id:
                            order.lead_id = amo_crm_lead_id
                            order.save(update_fields=['lead_id'])
                        if contact_id:
                            user = order.telegram_user
                            user.amo_contact_id = contact_id
                            user.save(update_fields=['amo_contact_id'])

                    kb_builder = KeyboardBuilder()
                    buttons_list = [
                        types.InlineKeyboardButton("🏠 Меню",
                                                   callback_data="menu"),
                    ]
                    kb_builder.add_rows(buttons_list, row_width=1)
                    keyboard = kb_builder.build()
                    bot.send_message(
                        chat_id=order.telegram_user.telegram_id,
                        text="Спасибо за сделанный заказ! Скоро с вами свяжутся!",
                        reply_markup=keyboard
                    )
                    logger.info(f'Осуществлен платеж ID {obj.id} по транзакции {obj.payment_id}')

            if notification_object.event == 'payment.canceled':
                obj = Transaction.objects.filter(payment_id=payment.id).exclude(status=PaymentStatus.SUCCESS).first()
                if obj:
                    obj.status = PaymentStatus.ERROR
                    obj.idempotence_key = None
                    obj.error_description = payment.cancellation_details.reason
                    obj.save(update_fields=['status', 'error_description', 'idempotence_key'])
                    order = obj.order
                    order.status = OrderStatus.CANCELED
                    order.save(update_fields=['status'])
                    bot = TelegramBot(order.bot_instance).bot
                    kb_builder = KeyboardBuilder()
                    buttons_list = [
                        types.InlineKeyboardButton("🏠 Меню",
                                                   callback_data="menu"),
                    ]
                    kb_builder.add_rows(buttons_list, row_width=1)
                    keyboard = kb_builder.build()
                    bot.send_message(
                        chat_id=order.telegram_user.telegram_id,
                        text="Заказ был отменен",
                        reply_markup=keyboard
                    )
                    logger.info(f'Отменен платеж ID {obj.id} по транзакции {obj.payment_id}')

        except Exception as exc:
            notification_object = WebhookNotification(data)
            payment = notification_object.object
            order = Transaction.objects.filter(payment_id=payment.id).first().order
            bot = TelegramBot(order.bot_instance).bot
            kb_builder = KeyboardBuilder()
            buttons_list = [
                types.InlineKeyboardButton("🏠 Меню",
                                           callback_data="menu"),
            ]
            kb_builder.add_rows(buttons_list, row_width=1)
            keyboard = kb_builder.build()
            bot.send_message(
                chat_id=order.telegram_user.telegram_id,
                text="Ошибка обработки платежа",
                parse_mode="HTML",
                reply_markup=keyboard
            )
            logger.error('Ошибка обработки вебхука: {exc}\ndata\n{data}'.format(exc=exc, data=data))

        return Response(status=status.HTTP_200_OK)
