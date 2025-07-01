import abc
import uuid

from django.conf import settings
from yookassa import Configuration


def get_config(account_id: str, secret_key: str):
    """Получение конфигурации сервиса."""
    return Configuration.configure(account_id, secret_key)


class BaseYooKassaService(abc.ABC):
    """Абстрактный класс работы с YooKassa."""

    ACCOUNT_ID: str
    SECRET_KEY: str
    CURRENCY = settings.YOOKASSA_CURRENCY

    def __init__(self, source_obj, redirect_url):
        self.source_obj = source_obj
        self._config = get_config(self.ACCOUNT_ID, self.SECRET_KEY)
        self._idempotence_key = None
        self.redirect_url = redirect_url
        self._data = {}

    @property
    def idempotence_key(self):
        if not self._idempotence_key:
            self._idempotence_key = self._get_idempotence_key()

        return self._idempotence_key

    def _get_idempotence_key(self):
        """Получение/создание ключа идемпотентности."""
        if not self.source_obj.idempotence_key:
            self.source_obj.idempotence_key = str(uuid.uuid4())
            self.source_obj.save(update_fields=['idempotence_key'])

        return self.source_obj.idempotence_key

    @property
    def data(self):
        if not self._data:
            self._data = self.collect_data()

        return self._data

    @abc.abstractmethod
    def collect_data(self):
        """Сбор полезной нагрузки для операции."""

    @abc.abstractmethod
    def execute(self):
        """Основной метод выполнения операции."""
