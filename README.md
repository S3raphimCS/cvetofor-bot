# cvetofor-bot

## Используемые технологии

Бэкенд: python3.10, django, django-rest-framework, pyTelegramBotAPI, redis

СУБД: PostgreSQL

Линтеры: isort, flake8

## Настройка проекта

Проект настраивается через переменные окружения, указанные в файле .env

Пример .env файла указан в .env.example

| Ключ                                         | Значение/Описание                                                    | По умолчанию (пример)       |
|:---------------------------------------------|:---------------------------------------------------------------------|:----------------------------|
| **`ENVIRONMENT`**                            | Окружение, в котором запускается приложение (development/production) | `development`               |
| **`LOCAL_DEV`**                              | Флаг, указывающий на локальную разработку                            | `TRUE`                      |
| **`ADMIN_LIST_FACTOR`**                      | Коэффициент или параметр, связанный с админ-панелью                  | `5`                         |
| **`PIPENV_IGNORE_VIRTUALENVS`**              | Флаг для Pipenv, чтобы игнорировать существующие venv                | `1`                         |
|                                              |                                                                      |                             |
| **`SECRET_KEY`**                             | Секретный ключ Django                                                | `super-insecure-django-key` |
| **`DEBUG`**                                  | Режим отладки Django                                                 | `True`                      |
| **`ALLOWED_HOSTS`**                          | Список разрешенных хостов                                            | `*`                         |
| **`ENV_NAME`**                               | Имя текущего окружения                                               | `DEV`                       |
|                                              |                                                                      |                             |
| **`POSTGRES_DB`**                            | Имя базы данных                                                      | `cvetoforbot`               |
| **`POSTGRES_USER`**                          | Имя пользователя для подключения к БД                                | `postgres`                  |
| **`POSTGRES_PASSWORD`**                      | Пароль пользователя для подключения к БД                             | `postgres`                  |
| **`POSTGRES_HOST`**                          | Адрес (хост) сервера базы данных                                     | `localhost`                 |
| **`POSTGRES_PORT`**                          | Порт сервера базы данных                                             | `5432`                      |
|                                              |                                                                      |                             |
| **`REMOTE_POSTGRES_DB`**                     | Имя удаленной базы данных                                            | `cv1`                       |
| **`REMOTE_POSTGRES_USER`**                   | Имя пользователя удаленной БД                                        | `postgres`                  |
| **`REMOTE_POSTGRES_PASSWORD`**               | Пароль пользователя удаленной БД                                     | `postgres`                  |
| **`REMOTE_POSTGRES_HOST`**                   | Адрес (хост) удаленной БД                                            | `localhost`                 |
| **`REMOTE_POSTGRES_PORT`**                   | Порт удаленной БД                                                    | `5432`                      |
|                                              |                                                                      |                             |
| **Настройки Redis**                          |                                                                      |                             |
| **`REDIS_HOST`**                             | Адрес (хост) сервера Redis                                           | `localhost`                 |
| **`REDIS_PORT`**                             | Порт сервера Redis                                                   | `6379`                      |
|                                              |                                                                      |                             |
| **Суперпользователь**                        |                                                                      |                             |
| **`SUPERUSER_EMAIL`**                        | Email для создаваемого суперпользователя                             | `superuser@example.com`     |
|                                              |                                                                      |                             |
| **Токены Telegram-ботов**                    |                                                                      |                             |
| **`ULAN_UDE_TOKEN`**                         | Токен Telegram-бота для Улан-Удэ                                     | получить у @BotFather       |
| **`ANGARSK_TOKEN`**                          | Токен Telegram-бота для Ангарска                                     | получить у @BotFather       |
| **`ANGARSK_GROUP_ID`**                       | ID группы в Telegram для Ангарска                                    | требуется заполнить         |
|                                              |                                                                      |                             |
| **Настройки ЮКасса**                         |                                                                      |                             |
| **`YOOKASSA_PAYMENT_SECRET_KEY`**            | Секретный ключ магазина ЮКасса                                       | получить в ЛК ЮКасса        |
| **`YOOKASSA_SHOP_ID`**                       | Идентификатор магазина (shopId) в ЮКасса                             | получить в ЛК ЮКасса        |
| **`YOOKASSA_PAYMENT_ANGARSK_REDIRECT_URL`**  | URL для возврата после оплаты (Ангарск)                              | требуется заполнить         |
| **`YOOKASSA_PAYMENT_ULAN_UDE_REDIRECT_URL`** | URL для возврата после оплаты (Улан-Удэ)                             | требуется заполнить         |
|                                              |                                                                      |                             |
| **Настройки amoCRM**                         |                                                                      |                             |
| **`AMOCRM_SUBDOMAIN`**                       | Поддомен аккаунта в amoCRM                                           | требуется заполнить         |
| **`AMOCRM_CLIENT_ID`**                       | ID интеграции amoCRM                                                 | получить в ЛК amoCRM        |
| **`AMOCRM_CLIENT_SECRET`**                   | Секретный ключ интеграции amoCRM                                     | получить в ЛК amoCRM        |
| **`AMOCRM_REDIRECT_URI`**                    | URL для редиректа после авторизации в amoCRM                         | требуется заполнить         |
| **`AMOCRM_ACCESS_TOKEN`**                    | Токен доступа amoCRM                                                 |                             |
| **`AMOCRM_REFRESH_TOKEN`**                   | Токен для обновления `access_token` amoCRM                           |                             |
|                                              |                                                                      |                             |
| **Настройки сервера**                        |                                                                      |                             |
| **`PATH_TO_MEDIA_ON_SERVER`**                | Абсолютный путь к медиа-папке на сервере                             | `/var/www/project/media`    |

**Локальный разворот проекта**:

1) В директории проекта создать виртуальное окружение python3.10:
   `python3.10 -m venv venv`
2) Активировать виртуальное окружение:
   `. venv/bin/activate` для Linux или `.\venv\Scripts\activate` для Windows
3) Установить зависимости для проекта `pip install -r src/requirements.txt`
4) Соберите статичные файлы `python manage.py collectstatic`
5) Запустить django миграции: `python manage.py migrate`
6) Подгрузите объекты ботов в админку `python manage.py loaddata Cvetoforbots/apps/core/fixtures/botinstance.json`
7) Загрузка старой базы пользователей `python manage.py load_users Cvetoforbots/apps/core/fixtures/users.json`
8) Создать celery-таски `python manage.py setuptasks`
9) Создать суперпользователя django: `python manage.py createsuperuser` (для использования в локальной разработке)
10) Запустить django server: `python manage.py runserver`

Боты запускаются через Django-Админку.

Проверка на линтеры, перейти в папку src:

1) `flake8`
2) `isort .`