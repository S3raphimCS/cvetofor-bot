import json
from django.core.management.base import BaseCommand
from django.db import transaction
from CvetoforBots.apps.core.models import TelegramUser, BotInstance


class Command(BaseCommand):
    help = 'Загружает пользователей из указанного JSON файла в базу данных'

    def add_arguments(self, parser):
        # Добавляем обязательный аргумент - путь к файлу
        parser.add_argument('json_file_path', type=str, help='Путь к JSON файлу с контактами')

    @transaction.atomic
    def handle(self, *args, **options):
        file_path = options['json_file_path']
        self.stdout.write(self.style.SUCCESS(f'Начинаем загрузку данных из файла: {file_path}'))

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR('Файл не найден. Пожалуйста, проверьте путь.'))
            return
        except json.JSONDecodeError as excp:
            self.stderr.write(self.style.ERROR(f'Ошибка декодирования JSON. Проверьте формат файла. {excp}'))
            return

        created_count = 0
        updated_count = 0
        ulan_ude_bot = BotInstance.objects.filter(title__icontains="улан").first()
        angarsk_bot = BotInstance.objects.filter(title__icontains="ангарс").first()

        for item in data:
            user, created = TelegramUser.objects.update_or_create(
                telegram_id=item["fields"].get('telegram_id'),
                username=item["fields"].get("username") if item["fields"].get("username") != "" else None,
                bot=ulan_ude_bot if item["fields"].get("bot", 1) == 1 else angarsk_bot,
                is_active=True
            )

            if created:
                created_count += 1
                self.stdout.write(f'  Создан новый контакт: {user.telegram_id}')
            else:
                updated_count += 1
                self.stdout.write(f'  Обновлен контакт: {user.telegram_id}')

        self.stdout.write(self.style.SUCCESS(
            f'\nЗагрузка завершена! Создано: {created_count}, Обновлено: {updated_count}.'
        ))
