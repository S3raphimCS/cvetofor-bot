from django.contrib import admin

from CvetoforBots.apps.mailing.models import Mailing, MailingLog


class MailingLogInline(admin.TabularInline):
    model = MailingLog
    extra = 0


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):

    list_display = ["title", "is_processed"]
    # inlines = [MailingLogInline]
    # Пока что убрал. Из-за большого кол-ва логов сильно лагает страница
    readonly_fields = ["is_processed"]
