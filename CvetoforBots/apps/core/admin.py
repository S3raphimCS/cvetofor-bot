from django.contrib import admin
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.urls import path, reverse
from django.utils.html import format_html
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.apps import apps
from CvetoforBots.apps.core.models import BotInstance, PDFDocument, TelegramUser
from CvetoforBots.apps.orders.models import Order
from django_celery_beat.models import (
    PeriodicTask,
    IntervalSchedule,
    CrontabSchedule,
    SolarSchedule,
    ClockedSchedule,
)

admin.site.unregister(User)
app = apps.get_app_config('auth')
app.verbose_name = 'Администраторы ботов'


# Unregister Celery
models_to_unregister = [
    PeriodicTask,
    IntervalSchedule,
    CrontabSchedule,
    SolarSchedule,
    ClockedSchedule,
]
for model in models_to_unregister:
    try:
        admin.site.unregister(model)
    except admin.sites.NotRegistered:
        pass


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs.model._meta.verbose_name = "Администратор"
        qs.model._meta.verbose_name_plural = "Администраторы"
        return qs


@admin.register(PDFDocument)
class PDFDocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'file')
    exclude = ('slug',)


@admin.register(BotInstance)
class BotInstanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'status', 'started_at', 'down_at', 'actions_column')
    readonly_fields = ('status', 'pid', 'started_at', 'down_at')
    exclude = ('status', 'started_at', 'down_at', 'token')
    actions = None
    ordering = ('id',)

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:bot_id>/run/',
                self.admin_site.admin_view(self.run_bot_view),
                name='run-bot'
            ),
            path(
                '<int:bot_id>/stop/',
                self.admin_site.admin_view(self.stop_bot_view),
                name='stop-bot'
            ),
        ]
        return custom_urls + urls

    def run_bot_view(self, request, bot_id):
        from CvetoforBots.apps.core.services import BotService
        bot = self.get_object(request, bot_id)
        BotService(bot).start()
        return HttpResponseRedirect(reverse('admin:core_botinstance_changelist'))

    def stop_bot_view(self, request, bot_id):
        from CvetoforBots.apps.core.services import BotService
        bot = self.get_object(request, bot_id)
        BotService(bot).stop()
        return HttpResponseRedirect(reverse('admin:core_botinstance_changelist'))

    def actions_column(self, obj):
        if obj.status == 'running':
            return format_html(
                '<a class="btn btn-danger" href="{}">Остановить</a>',
                reverse(
                    'admin:stop-bot',
                    args=[obj.pk]
                )
            )
        else:
            return format_html(
                '<a class="btn btn-success" href="{}">Запустить</a>',
                reverse(
                    'admin:run-bot',
                    args=[obj.pk]
                )
            )

    actions_column.short_description = 'Действия'


class UserOrderInline(admin.StackedInline):
    model = Order
    extra = 0


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):

    inlines = [UserOrderInline]


admin.site.unregister(Group)
