from django.conf import settings
from loguru import logger
from yookassa import Payment

from CvetoforBots.apps.flowers.models import GroupProduct
from CvetoforBots.apps.transactions.enums import PaymentStatus
from CvetoforBots.services.payments.base import BaseYooKassaService


class PaymentService(BaseYooKassaService):
    """Класс-сервис получения ссылки на оплату."""

    ACCOUNT_ID = settings.YOOKASSA_SHOP_ID
    SECRET_KEY = settings.YOOKASSA_PAYMENT_SECRET_KEY

    def collect_data(self):
        """Сбор полезной нагрузки для операции."""
        data = {
            'amount': {
                'value': str(self.source_obj.amount),
                'currency': self.CURRENCY
            },
            'confirmation': {
                'type': 'redirect',
                'return_url': self.redirect_url,
            },
            'description': self.source_obj.description,
            'capture': True,
            "receipt": {
                "customer": {
                    "phone": self.source_obj.order.user_contact,
                },
                "tax_system_code": 2,
                "items": [
                    {
                        "quantity": 1,
                        "description": GroupProduct.objects.get(id=self.source_obj.order.group_product_id).title,
                        "amount": {
                            "value": str(self.source_obj.order.amount),
                            "currency": self.CURRENCY
                        },
                        "vat_code": 7,
                    }
                ]

            }
        }
        return data

    def execute(self):
        """Основной метод выполнения операции."""
        url = ''

        try:
            payment = Payment.create(self.data, self.idempotence_key)
            self.source_obj.payment_id = payment.id
            self.source_obj.save(update_fields=['payment_id'])
            url = payment.confirmation.confirmation_url
        except Exception as exc:
            logger.error('Ошибка формирования платежа ЮКасса: {exc}'.format(exc=exc))
            self.source_obj.status = PaymentStatus.ERROR
            self.source_obj.error_description = exc.content.get('description', exc)
            self.source_obj.idempotence_key = None
            self.source_obj.save(update_fields=['status', 'error_description', 'idempotence_key'])

        return url
