from django.db import models


class City(models.Model):
    id = models.AutoField(db_column="id", primary_key=True)
    name = models.CharField(max_length=200, db_column="city")
    deleted_at = models.DateTimeField(db_column="deleted_at", null=True)

    class Meta:
        db_table = 'cities'
        managed = False

    def __str__(self):
        return str(self.id) + " " + (self.name if self.name else "")


class Market(models.Model):

    id = models.AutoField(db_column="id", primary_key=True)
    name = models.CharField(max_length=200, db_column="name")
    city = models.ForeignKey(City, on_delete=models.DO_NOTHING, db_column="city_id", null=True, blank=True)
    deleted_at = models.DateTimeField(db_column="deleted_at", null=True, blank=True)

    def __str__(self):
        return str(f"{self.city} - {self.name}")

    class Meta:
        db_table = 'markets'
        managed = False


class Category(models.Model):
    """Модель категории товара из удаленной БД"""

    id = models.AutoField(db_column="id", primary_key=True)
    title = models.CharField(max_length=200, db_column="title")
    deleted_at = models.DateTimeField(db_column="deleted_at")

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'categories'
        managed = False
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Product(models.Model):
    """Модель товара из удаленной БД"""

    id = models.AutoField(db_column="id", primary_key=True)
    title = models.CharField(max_length=200, db_column="title")
    description = models.TextField(db_column='description', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING, db_column='category_id', null=True, blank=True)
    market = models.ForeignKey(Market, on_delete=models.DO_NOTHING, db_column='market_id', null=True, blank=True)
    is_market_public = models.BooleanField(default=False, db_column='is_market_public')
    deleted_at = models.DateTimeField(db_column='deleted_at', null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'products'
        managed = False
        verbose_name = "Товар"
        verbose_name_plural = "Товары"


class GroupProductCategory(models.Model):
    id = models.AutoField(db_column="id", primary_key=True)
    title = models.CharField(max_length=200, db_column="title")
    deleted_at = models.DateTimeField(db_column="deleted_at", null=True, blank=True)

    def __str__(self):
        return str(self.id) + " " + self.title

    class Meta:
        db_table = 'group_product_categories'
        managed = False


class GroupProductCategorySlug(models.Model):
    id = models.AutoField(db_column="id", primary_key=True)
    group_product_category = models.ForeignKey(GroupProductCategory, on_delete=models.DO_NOTHING, null=True, blank=True)
    slug = models.CharField(max_length=200, db_column="slug")
    deleted_at = models.DateTimeField(db_column='deleted_at', null=True, blank=True)

    def __str__(self):
        return str(self.id) + " " + self.slug

    class Meta:
        db_table = 'group_product_category_slugs'
        managed = False


class GroupProduct(models.Model):
    id = models.AutoField(db_column="id", primary_key=True)
    title = models.CharField(max_length=200, db_column="title")
    deleted_at = models.DateTimeField(db_column='deleted_at', null=True, blank=True)
    description = models.TextField(db_column='description', null=True, blank=True)
    is_public = models.BooleanField(default=False, db_column='is_public')
    category = models.ForeignKey(GroupProductCategory, on_delete=models.DO_NOTHING, db_column='category_id', related_name='group_products', null=True)
    created_by_market_id = models.ForeignKey(Market, on_delete=models.DO_NOTHING, db_column='created_by_market_id', null=True)
    published = models.BooleanField(db_column='published', null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'group_products'
        managed = False
        verbose_name = "Группа товаров"
        verbose_name_plural = "Группы товаров"


class ProductPrice(models.Model):
    """Модель цены товара из удаленной БД"""

    id = models.AutoField(db_column="id", primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING, db_column="product_id", related_name="prices", null=True)
    group_product = models.ForeignKey(GroupProduct, on_delete=models.DO_NOTHING, db_column="group_product_id", related_name="prices", null=True)
    price = models.DecimalField(db_column="price", decimal_places=2, max_digits=8)
    market = models.ForeignKey(Market, on_delete=models.DO_NOTHING, db_column="market_id")
    deleted_at = models.DateTimeField(db_column="deleted_at", null=True)

    def __str__(self):
        return f"{self.product} - {self.price}"

    class Meta:
        db_table = 'product_prices'
        managed = False
        verbose_name = "Цена товара"
        verbose_name_plural = "Цены товаров"


class Blocks(models.Model):

    id = models.AutoField(db_column="id", primary_key=True)
    blockable_id = models.IntegerField(db_column="blockable_id", null=True)
    blockable_type = models.CharField(max_length=200, db_column="blockable_type", null=True)
    position = models.IntegerField(db_column="position", null=True)
    content = models.TextField(db_column="content", null=True)

    class Meta:
        managed = False
        db_table = 'blocks'
        verbose_name = 'Блок'
        verbose_name_plural = 'Блоки'


class Color(models.Model):
    id = models.AutoField(db_column="id", primary_key=True)
    title = models.CharField(max_length=200, db_column="title")
    deleted_at = models.DateTimeField(db_column='deleted_at', null=True, blank=True)

    def __str__(self):
        return self.title if self.title else str(self.id)

    class Meta:
        managed = False
        db_table = 'colors'
        verbose_name = "Цвет"
        verbose_name_plural = "Цвета"


class Media(models.Model):
    id = models.AutoField(db_column="id", primary_key=True)
    deleted_at = models.DateTimeField(db_column='deleted_at', null=True, blank=True)
    uuid = models.TextField(db_column='uuid', null=True)

    class Meta:
        managed = False
        db_table = 'medias'


class Mediable(models.Model):
    id = models.AutoField(db_column="id", primary_key=True)
    deleted_at = models.DateTimeField(db_column='deleted_at', null=True, blank=True)
    media = models.ForeignKey(Media, on_delete=models.DO_NOTHING, db_column='media_id', null=True)
    mediable_id = models.IntegerField(db_column='mediable_id', null=True)
    mediable_type = models.CharField(max_length=200, db_column='mediable_type', null=True)

    class Meta:
        managed = False
        db_table = "mediables"
