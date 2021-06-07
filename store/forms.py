from django.forms import ModelForm

from django import forms

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import *


class OrderForm(ModelForm):
    class Meta:
        model = ShippingAdress
        fields = ('__all__')


class CreateUserForm(UserCreationForm):
    phone = forms.CharField()
    first_name = forms.CharField()
    # last_name = forms.CharField()

    class Meta:
        model = User
        fields = ['username', 'first_name', 'phone', 'password1', 'password2']


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ('__all__')


class CategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = ('__all__')


class SubCategoryForm(ModelForm):
    class Meta:
        model = SubCategory
        fields = ('__all__')


class SizeForm(ModelForm):
    class Meta:
        model = Product
        fields = ('size',)
# class SizeProduct(ModelForm):
#     class Meta:
#         model = Product
#         fields = ['size']
