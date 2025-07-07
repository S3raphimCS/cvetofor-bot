from django.contrib import admin
from django.utils.html import format_html

from CvetoforBots.apps.flowers.models import GroupProduct
from CvetoforBots.apps.orders.models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_name', 'display_product_name')
    list_display_links = ('id', 'display_product_name')

    fields = (
        'telegram_user', "user_name", "user_contact", "recipient_name", "recipient_phone", "recipient_address",
        "status", "lead_id", "compound", "delivery_date", "time_interval",
        "amount", "with_post_card", "post_card_text", "bot_instance", 'display_group_product_name_on_form'
    )

    readonly_fields = ("lead_id", 'display_group_product_name_on_form',)

    def display_product_name(self, obj):
        if hasattr(obj, 'group_product_id'):
            return GroupProduct.objects.get(id=obj.group_product_id)
        return f"Товар с ID {obj.group_product_id} не найден"

    display_product_name.short_description = 'Название товара'
    display_product_name.admin_order_field = 'group_product_id'

    def display_group_product_name_on_form(self, obj):
        """
        Метод для отображения названия и ссылки на товар на странице заказа.
        """
        if not obj:
            return "Товар будет определен после сохранения"

        try:
            product = GroupProduct.objects.get(id=obj.group_product_id)
            return product.title
        except GroupProduct.DoesNotExist:
            return f"Товар с ID {obj.product_id} не найден"

    display_group_product_name_on_form.short_description = 'Информация о товаре'
