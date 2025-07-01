from django.contrib import admin

from CvetoforBots.apps.flowers.models import (
    Category,
    City,
    GroupProduct,
    GroupProductCategory,
    GroupProductCategorySlug,
    Market,
    Product,
    ProductPrice,
)


# @admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'category__title', "is_market_public",)
    search_fields = ("title", "category__title")
    readonly_fields = ("id",)
    fields = ("id", "title", "price", "category__title", "description", "is_market_public")

    def price(self, obj):
        return ProductPrice.objects.filter(product_id=obj.id, price__isnull=False).last().price

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# @admin.register(ProductPrice)
class ProductPriceAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# @admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# @admin.register(GroupProductCategory)
class GroupProductCategoryAdmin(admin.ModelAdmin):
    pass


# @admin.register(GroupProductCategorySlug)
class GroupProductCategorySlugAdmin(admin.ModelAdmin):
    pass


# @admin.register(Market)
class MarketAdmin(admin.ModelAdmin):
    pass


# @admin.register(City)
class CityAdmin(admin.ModelAdmin):
    search_fields = ["name"]


# @admin.register(GroupProduct)
class GroupProductAdmin(admin.ModelAdmin):

    search_fields = ["title"]
