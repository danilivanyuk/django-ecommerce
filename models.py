from django.db.models import Sum
from django.db import models
from django.contrib.auth.models import User
from multiselectfield import MultiSelectField
import datetime
from datetime import timedelta
from django.utils import timezone

from io import BytesIO
from PIL import Image
from django.core.files import File


class Customer(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=200)

    def __str__(self):
        return self.name

    def customers_count(self):
        total = len(self.user)
        return total


CLOTH_SIZE = [
    ("XS", 'XS'),
    ("S", 'S'),
    ("M", 'M'),
    ("L", 'L'),
    ("XL", 'XL'),
    ("XXL", 'XXL'),
]


GENDER_CHOICES = (
    ('man', 'Мужской'),
    ('women', 'Женский'),
    ('kid', 'Детский'),
)


SEASON_CHOICES = (
    ('summer', 'Лето'),
    ('autumn ', 'Осень'),
    ('winter ', 'Зима'),
    ('spring  ', 'Весна'),
)


class Category(models.Model):
    name = models.CharField(
        max_length=100, verbose_name="Название категории", db_index=True)
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Создано: ")
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Обновлено: ")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-name']
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class SubCategory(models.Model):
    category = models.ForeignKey(
        Category, related_name='subcategories', on_delete=models.CASCADE, verbose_name="Категория", default=None)
    name = models.CharField(
        max_length=100, verbose_name="Название подкатегории")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-name']
        verbose_name = "Подкатегория"
        verbose_name_plural = "Подкатегории"


def compress(image):
    im = Image.open(image)
    # create a BytesIO object
    im_io = BytesIO()
    # save image to BytesIO object
    im.save(im_io, 'JPEG', optimize=True, quality=70)
    # create a django-friendly Files object
    new_image = File(im_io, name=image.name)
    return new_image


class Product(models.Model):
    subcategory = models.ForeignKey(
        SubCategory, on_delete=models.CASCADE, verbose_name='Подкатегория')
    title = models.CharField(max_length=60, verbose_name='Название')
    gender = models.CharField(
        max_length=30, choices=GENDER_CHOICES, default='man', verbose_name='Пол')

    size = MultiSelectField(choices=CLOTH_SIZE, blank=True,
                            null=True, verbose_name='Размеры')

    image = models.ImageField(blank=True, null=True,
                              verbose_name="Изображение")
    price = models.IntegerField(blank=True, null=True, verbose_name="Цена")
    # price = models.DecimalField( max_digits=7 ,verbose_name="Цена")

    description = models.TextField(
        blank=True, null=True, verbose_name="Описание")
    availability = models.BooleanField(default=True, verbose_name="Наличие")

    madeOf = models.CharField(
        max_length=60, blank=True, null=True, verbose_name='Состав')
    season = models.CharField(
        max_length=30, choices=SEASON_CHOICES, default='man', verbose_name='Сезон')

    color = models.CharField(max_length=50, blank=True,
                             null=True, verbose_name="Цвет")
    country = models.CharField(
        max_length=50, blank=True, null=True, verbose_name='Страна производства:')
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Создано: ")
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Обновлено: ")

    def __str__(self):
        return self.name

    # SAVE METHOD

    def save(self, *args, **kwargs):
        # call the compress function
        new_image = compress(self.image)
        # set self.image to new_image
        self.image = new_image
        # save
        super().save(*args, **kwargs)

    def flavor_verbose(self):
        return dict(GENDER_CHOICES)[self.gender]

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url

    class Meta:
        ordering = ['-title']
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return self.title


class Order(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, blank=True, null=True)
    ordered_date = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата заказа")
    complete = models.BooleanField(default=False, verbose_name='Заказан')
    finished = models.BooleanField(default=False, verbose_name='Завершен')

    transaction_id = models.CharField(max_length=200, null=True)

    @property
    def get_address(self):
        address = self.shippingadress_set.all()
        return address

    def get_nonfinished_orders(self):
        a = []
        if self.finished != True:
            a.append(self)
        return a

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ['-ordered_date']
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def get_finished_orders(self):
        orderproducts = self.orderproduct_set.all()
        return orderproducts

    def get_proceeds(self):
        total = self.get_finished_orders
        return total

    @ property
    def get_cart_total(self):
        orderproducts = self.orderproduct_set.all()
        total = sum([product.get_total for product in orderproducts])
        return total

    @ property
    def get_cart_items(self):
        orderproducts = self.orderproduct_set.all()
        total = sum([product.quantity for product in orderproducts])
        return total

    def if_less_then_24(self):
        return self.ordered_date + timedelta(hours=24) < timezone.now()


class OrderProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    size = models.CharField(choices=CLOTH_SIZE, blank=True,
                            null=True, verbose_name='Размеры', max_length=50)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.order)

    @ property
    def get_total(self):
        total = self.product.price * self.quantity
        return total

    class Meta:
        ordering = ['-product']
        verbose_name = "Order Products"
        verbose_name_plural = "Order Products"


class ShippingAdress(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    city = models.CharField(max_length=200, null=False)
    street = models.CharField(max_length=200, null=False)
    house = models.CharField(max_length=200, null=False)
    appartament = models.CharField(max_length=200, null=False)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (self.city + ', ' + self.street + ' ' + self.house + ', ' + self.appartament)

    class Meta:
        verbose_name = 'Адрес'
        verbose_name_plural = 'Адреса'
