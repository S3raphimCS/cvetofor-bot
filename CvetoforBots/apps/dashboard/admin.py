from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode

from CvetoforBots.apps.core.models import TelegramUser
from CvetoforBots.apps.dashboard.models import Dashboard
from CvetoforBots.apps.orders.enums import OrderStatus
from CvetoforBots.apps.orders.models import Order


@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):

    def get_queryset(self, request):
        return ContentType.objects.none()

    def changelist_view(self, request, extra_context=None):
        # 1. Считаем статистику (как и раньше)
        completed_orders_count = Order.objects.filter(
            status__in=[
                OrderStatus.PAID.value, OrderStatus.DONE.value,
                OrderStatus.NEW.value, OrderStatus.IN_WORK.value
            ]
        ).count()
        total_users_count = TelegramUser.objects.count()
        active_users_count = TelegramUser.objects.filter(is_active=True).count()
        inactive_users_count = total_users_count - active_users_count

        # 2. Создаем URL-ы для каждой метрики

        # URL для заказов
        order_changelist_url = reverse('admin:orders_order_changelist')
        # Создаем параметры фильтра
        order_params = urlencode({
            'status__in': ','.join([
                OrderStatus.PAID.value, OrderStatus.DONE.value,
                OrderStatus.NEW.value, OrderStatus.IN_WORK.value
            ])
        })
        # Формируем полную ссылку
        completed_orders_link = f'{order_changelist_url}?{order_params}'

        # URL для пользователей
        user_changelist_url = reverse('admin:core_telegramuser_changelist')
        # Ссылка на всех пользователей
        total_users_link = user_changelist_url
        # Ссылка на активных
        active_users_link = f'{user_changelist_url}?is_active__exact=1'
        # Ссылка на неактивных
        inactive_users_link = f'{user_changelist_url}?is_active__exact=0'

        # 3. Формируем новый контекст с HTML-ссылками
        extra_context = extra_context or {}
        extra_context['stats_data'] = {
            'Совершенных заказов': format_html('<a href="{}">{}</a>', completed_orders_link, completed_orders_count),
            'Всего пользователей в базе': format_html('<a href="{}">{}</a>', total_users_link, total_users_count),
            'Активных пользователей': format_html('<a href="{}">{}</a>', active_users_link, active_users_count),
            'Пользователей вышли из бота': format_html('<a href="{}">{}</a>', inactive_users_link,
                                                       inactive_users_count),
        }

        # Меняем заголовок страницы
        extra_context['title'] = "Ключевые метрики бота"

        return super().changelist_view(request, extra_context=extra_context)

    def has_add_permission(self, request):
        return False
