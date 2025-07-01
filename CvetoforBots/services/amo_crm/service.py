import datetime

from django.conf import settings
from loguru import logger
import requests
from zoneinfo import ZoneInfo

from CvetoforBots.apps.transactions.models import AmoCRM


class AmoCRMWrapper:
    def __init__(self):
        self.amo_crm_instance = AmoCRM.get_solo()
        self.access_token = self.amo_crm_instance.access_token
        self.refresh_token = self.amo_crm_instance.refresh_token

    def renew_tokens(self) -> None:
        url = f"https://{settings.AMOCRM_SUBDOMAIN}.amocrm.ru/oauth2/access_token"
        headers = {
            'Content-Type': 'application/json'
        }
        data = {
            "client_id": settings.AMOCRM_CLIENT_ID,
            "client_secret": settings.AMOCRM_CLIENT_SECRET,
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "redirect_uri": settings.AMOCRM_REDIRECT_URI
        }
        response = requests.post(url, headers=headers, json=data).json()
        self.amo_crm_instance.access_token = response["access_token"]
        self.amo_crm_instance.refresh_token = response["refresh_token"]
        self.amo_crm_instance.save(update_fields=["access_token", "refresh_token"])
        self.access_token = self.amo_crm_instance.access_token
        self.refresh_token = self.amo_crm_instance.refresh_token

    def create_lead(self, name: str, phone: str, price: int, tg_username: str, tg_id: int, recipient_name: str,
                    recipient_phone: str,
                    recipient_address: str, bouquet_name: str, order_composition: str,
                    delivery_date: datetime.date, time_interval: str, post_card_text=None,
                    contact=None, is_renewed=False) -> (int | None, int | None):
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            custom_fields_values = [
                {
                    "field_id": 667625,  # Предоплата
                    "values": [
                        {
                            "value": f"{price}"
                        }
                    ]
                },
                {
                    "field_id": 667723,  # Оплачено безналом
                    "values": [
                        {
                            "value": f"{price}"
                        }
                    ]
                },
                {
                    "field_id": 667627,  #
                    "values": [
                        {
                            "value": "Безнал",
                            "enum_id": 762735,
                        }
                    ]
                },
                {
                    "field_id": 449403,
                    "values": [
                        {
                            "value": f"{recipient_name}"  # Имя получателя
                        }
                    ]},
                {
                    "field_id": 449405,
                    "values": [
                        {
                            "value": f"{recipient_phone}"  # Телефон получателя
                        }
                    ]
                },
                {
                    "field_id": 479045,  # Адрес выдачи
                    "values": [
                        {
                            "value": "Геологическая 11а",
                            "enum_id": 808733,
                        }
                    ]
                },
                {
                    "field_id": 479055,
                    "values": [
                        {
                            "value": "Доставка",
                            "enum_id": 691625,
                        }
                    ]
                },
                {
                    "field_id": 449407,  # Адрес доставки
                    "values": [
                        {
                            "value": f"{recipient_address}"
                        }
                    ]
                },
                {
                    "field_id": 449439,
                    "values": [
                        {
                            "value": "Чат-Бот",
                            "enum_id": 748835,
                        }
                    ]
                },
                {
                    "field_id": 479061,  # Статус оплаты
                    "values": [
                        {
                            "value": "Оплачен",  # Тут надо предоплачено потом поменять
                            "enum_id": 691905,
                        }
                    ]
                },
                {
                    "field_id": 449441,  # Способ оплаты
                    "values": [
                        {
                            "value": "Юкасса",
                            "enum_id": 801191,
                        }
                    ]
                },
                {
                    "field_id": 659683,
                    "values": [
                        {
                            "value": f"{bouquet_name}"
                        }
                    ]
                },
                {
                    "field_id": 450561,  # Состав заказа
                    "values": [
                        {
                            "value": f"{order_composition}"
                        }
                    ]
                },
                {
                    "field_id": 507855,  # Стоимость в Чат-боте
                    "values": [
                        {
                            "value": f"{price}"
                        }
                    ]
                },
                {
                    "field_id": 449409,
                    "values": [
                        {
                            "value": f"{datetime.datetime.combine(delivery_date, datetime.time.min).replace(tzinfo=ZoneInfo('UTC'))}".replace(" ", "T", 1)
                        }
                    ]
                },
                {
                    "field_id": 693149,
                    "values": [
                        {
                            "value": f"{time_interval}"
                        }
                    ]
                }
            ]
            tags = [
                {
                    "id": 217391,
                    "name": "Чат-Бот",
                }
            ]
            if post_card_text:
                custom_fields_values.append(
                    {
                        "field_id": 450563,  # Комментарий к заказу
                        "values": [
                            {
                                "value": f"{post_card_text}"
                            }
                        ]
                    }
                )
            if not contact:
                contact = self.create_contact(name, phone, tg_username, tg_id)
            contacts = [
                {
                    "id": contact,
                    "is_main": True
                }
            ]
            data = [
                {
                    "phone": phone,
                    "price": price,
                    "pipeline_id": 3368875,
                    "status_id": 34210183,
                    "custom_fields_values": custom_fields_values,
                    "_embedded": {
                        "tags": tags,
                        "contacts": contacts
                    }
                }
            ]
            url = f"https://{settings.AMOCRM_SUBDOMAIN}.amocrm.ru/api/v4/leads"
            response = requests.post(url, headers=headers, json=data).json()
            if response.get("status", None) == 401:
                if is_renewed:
                    logger.error("Ошибка авторизации при создании сделки")
                    return None
                self.renew_tokens()
                return self.create_lead(name, phone, price, tg_username, tg_id, recipient_name,
                                        recipient_phone,
                                        recipient_address, bouquet_name, order_composition,
                                        delivery_date, time_interval, post_card_text, contact,
                                        is_renewed=True)
            return response["_embedded"]["leads"][0]["id"], contact
        except Exception as err:
            # logger.info(response)
            logger.error(err)

    def create_contact(self, name: str, phone: str, tg_username, tg_id, is_renewed=False) -> int | None:
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            url = f"https://{settings.AMOCRM_SUBDOMAIN}.amocrm.ru/api/v4/contacts"
            custom_fields_values = [
                {
                    "field_id": 147851,
                    "values": [
                        {
                            "value": f"{phone}",
                            "enum_id": 209691
                        }
                    ]
                },
                {
                    "field_id": 705585,  # Телеграм chat_id (Pact.im)
                    "values": [
                        {
                            "value": f"{tg_id}"
                        }
                    ]
                },
                {
                    "field_id": 703111,  # Телеграм Никнейм (Pact.im)
                    "values": [
                        {
                            "value": f"{tg_username}"
                        }
                    ]
                }
            ]
            data = [{
                "first_name": name,
                "custom_fields_values": custom_fields_values
            }]
            response = requests.post(url, headers=headers, json=data).json()
            if response.get("status", None) == 401:
                if is_renewed:
                    logger.error("Ошибка авторизации при создании контакта")
                    return None
                self.renew_tokens()
                return self.create_contact(name, phone, is_renewed=True)
            return response['_embedded']['contacts'][0]["id"]
        except Exception as err:
            # logger.info(response)
            logger.error(err)

# amocrm_wrapper_1 = AmoCRMWrapper()
# amocrm_wrapper_1.init_oauth2()
#
# if __name__ == "__main__":
#     amocrm_wrapper_1 = AmoCRMWrapper()
#
#     # print(amocrm_wrapper_1.get_lead_by_id(34819677))
#     print(amocrm_wrapper_1.add_lead(data={"add": [{"name": "Сделка с бота", "price": 1500}]}))
