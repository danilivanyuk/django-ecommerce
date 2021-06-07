import locale
from collections import deque
from dateutil.relativedelta import *
from django import template
from .decorators import *
from .utils import *
from .forms import *
from django.db.models import Count
from django.shortcuts import render, redirect
from .models import *
from django.http import JsonResponse, HttpResponseRedirect
import json
from datetime import datetime, timedelta
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from functools import reduce
import operator


@unauthenticated_user
def registerPage(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            customer = form.save()
            username = form.cleaned_data.get('username')
            Customer.objects.create(
                user=User.objects.get(username=username),
                name=form.cleaned_data.get('first_name'),
                phone=form.cleaned_data.get('phone')
            )
            return redirect('homepage')
    context = {'form': form}
    return render(request, 'store/register.html', context)


@unauthenticated_user
def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('homepage')
        else:
            print('username or password is incorrect')
    return render(request, 'store/login.html')


def logoutUser(request):
    logout(request)
    return redirect('homepage')


def homepage(request):
    data = cartData(request)
    cartItems = data['cartItems']
    products = Product.objects.all()[:10]
    categories = Category.objects.all()
    context = {
        'products': products, 'cartItems': cartItems, 'categories': categories,
    }
    return render(request, 'store/homepage.html', context)


def get_subcategories_of_products(products):
    subcategories = []
    for product in products:
        if product.subcategory not in subcategories:
            subcategories.append(product.subcategory)
    return subcategories


def search(request):
    search_input = request.GET.get('global-search')

    products = Product.objects.filter(
        Q(title__icontains=search_input) | Q(subcategory__name__icontains=search_input))

    a = get_subcategories_of_products(products)

    form = SizeForm()
    products_data = filterProducts(request, products)

    products = products_data['products']
    sizes = products_data['sizes']
    price_max = products_data['price_max']
    price_min = products_data['price_min']
    sort = products_data['sort_value']
    gender = products_data['gender']

    products = paginatorUtil(request, products)
    context = {'products': products, 'form': form, 'sizes': sizes, 'price_min': price_min,
               'price_max': price_max, 'sort_value': sort, 'gender': gender}
    return render(request, 'store/search_result.html', context)


@login_required(login_url='login')
def userProfile(request):
    orders = request.user.customer.order_set.all()
    order_products = OrderProduct.objects.filter(
        order__in=orders)

    context = {'orders': orders, 'order_products': order_products}
    return render(request, 'store/userProfile.html', context)


def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/cart.html', context=context)


def checkout(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/checkout.html', context=context)


def category(request, category_id):
    subcategories = SubCategory.objects.filter(category=category_id)
    category = Category.objects.get(pk=category_id)
    products = Product.objects.all()
    form = SizeForm()

    products_data = filterProducts(request, products)
    products = products_data['products']
    sizes = products_data['sizes']
    price_max = products_data['price_max']
    price_min = products_data['price_min']
    sort = products_data['sort_value']
    gender = products_data['gender']

    products = products.filter(
        reduce(lambda x, y: x | y, [Q(subcategory__name=item) for item in subcategories]))

    products = paginatorUtil(request, products)

    context = {'subcategories': subcategories,
               'category': category, 'products': products, 'form': form, 'sizes': sizes, 'price_min': price_min, 'price_max': price_max, 'sort_value': sort, 'gender': gender}
    return render(request, 'store/category.html', context)


# def is_valid_queryparam(param):
#     return param != '' and param is not None


def subcategory(request, subcategory_id):
    products = Product.objects.filter(subcategory=subcategory_id)

    form = SizeForm()

    products_data = filterProducts(request, products)

    products = products_data['products']
    sizes = products_data['sizes']
    price_max = products_data['price_max']
    price_min = products_data['price_min']
    sort = products_data['sort_value']
    gender = products_data['gender']

    current_subcategory = SubCategory.objects.get(pk=subcategory_id)
    category_of_subcategory = current_subcategory.category_id
    all_subcategory_products = SubCategory.objects.filter(
        category=category_of_subcategory)

    products = paginatorUtil(request, products)

    context = {'products': products,
               'current_subcategory': current_subcategory,
               'all_subcategory_products': all_subcategory_products,
               'form': form, 'sizes': sizes, 'price_min': price_min, 'price_max': price_max, 'sort_value': sort, 'gender': gender
               }

    return render(request, 'store/subcategory.html', context)


def product(request, product_id):
    product = Product.objects.get(pk=product_id)
    context = {'product': product}
    return render(request, 'store/product.html', context)


def cancelOrder(request):
    data = json.loads(request.body)
    productId = data['productId']
    order = data['order']
    product = Product.objects.get(id=productId)
    customer = request.user.customer
    orderproduct = OrderProduct.objects.get(product=product, order=order)
    orderproduct.delete()
    return JsonResponse('Order Canceled', safe=False)


def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    size = data['size']
    # cart_product_size = data['size']
    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(
        customer=customer, complete=False)
    orderProduct, created = OrderProduct.objects.get_or_create(
        order=order, product=product)
    orderProduct.size = size

    if action == 'add':
        orderProduct.quantity = (orderProduct.quantity + 1)
    elif action == 'remove':
        orderProduct.quantity = (orderProduct.quantity - 1)

    orderProduct.save()
    if orderProduct.quantity <= 0:
        orderProduct.delete()
    return JsonResponse('Item was added', safe=False)


def processOrder(request):
    transaction_id = datetime.now().timestamp()
    data = json.loads(request.body)
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)

    else:
        customer, order = guestOrder(request, data)
    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == float(order.get_cart_total):
        order.complete = True
    order.save()

    ShippingAdress.objects.get_or_create(
        customer=customer,
        order=order,
        city=data['shipping']['city'],
        street=data['shipping']['street'],
        house=data['shipping']['house'],
        appartament=data['shipping']['appartament']
    )
    return JsonResponse('Payment Complete', safe=False)


locale.setlocale(locale.LC_ALL, "ru_RU")


@admin_only
def adminPanel(request):

    data = adminPanelProducts(request)
    orders = data['orders']
    unfinished_orders_count = data['unfinished_orders_count']
    earnings_overview = adminPanelEarningsOverview(request)
    order_products = data['order_products']
    # shipping_adresses = data['shipping_adresses']
    months = earnings_overview['months']
    earnings_month_1 = earnings_overview['earnings_month_1']
    earnings_month_2 = earnings_overview['earnings_month_2']
    earnings_month_3 = earnings_overview['earnings_month_3']
    earnings_month_4 = earnings_overview['earnings_month_4']
    earnings_month_5 = earnings_overview['earnings_month_5']
    annual_earnings = earnings_overview['annual_earnings']

    total_customers = Customer.objects.aggregate(total=Count('user'))

    context = {'orders': orders,
               'order_products': order_products, 'months': months, 'earnings_month_1': earnings_month_1, 'earnings_month_2': earnings_month_2, 'earnings_month_3': earnings_month_3, 'earnings_month_4': earnings_month_4, 'earnings_month_5': earnings_month_5, 'annual_earnings': annual_earnings, 'unfinished_orders_count': unfinished_orders_count, 'total_customers': total_customers}
    return render(request, 'store/adminPanel/adminPanel.html', context)


@admin_only
def showAllCategories(request):
    categories = Category.objects.all()
    subcategories = SubCategory.objects.filter(category__in=categories)
    context = {'categories': categories, 'subcategories': subcategories}
    return render(request, 'store/adminPanel/all_categories.html', context)


@admin_only
def deleteSubCategory(request, subcategory_id):
    subcategory = SubCategory.objects.get(id=subcategory_id)
    products = Product.objects.filter(subcategory=subcategory)
    if request.method == 'POST':
        subcategory.delete()
        redirect('all_categories')
    context = {'subcategory': subcategory, 'products': products}
    return render(request, 'store/adminPanel/delete_category.html', context)


@admin_only
def deleteCategory(request, category_id):
    category = Category.objects.get(id=category_id)
    subcategories = SubCategory.objects.filter(category=category)
    if request.method == 'POST':
        category.delete()
        redirect('all_categories')
    context = {'category': category, 'subcategories': subcategories}
    return render(request, 'store/adminPanel/delete_category.html', context)


@admin_only
def unfinishedOrders(request):
    data = adminPanelProducts(request)
    unfinished_orders = data['unfinished_order']
    unfinished_orderProducts = OrderProduct.objects.filter(
        order__in=unfinished_orders)
    context = {'unfinished_orders': unfinished_orders,
               'unfinished_orderProducts': unfinished_orderProducts}
    return render(request, 'store/adminPanel/unfinished_orders.html', context)


@admin_only
def createProduct(request):
    form = ProductForm()
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('admin_panel')
    context = {'form': form}
    return render(request, 'store/adminPanel/create_product.html', context)


@admin_only
def showCustomers(request):
    customers = Customer.objects.all()
    context = {'customers': customers}
    return render(request, 'store/adminPanel/customers.html', context)


@admin_only
def showCustomerOrders(request, customer_id):
    orders = Order.objects.filter(customer=customer_id, complete=True)
    order_products = OrderProduct.objects.filter(
        order__in=orders)
    customer = Customer.objects.get(id=customer_id)
    context = {'orders': orders,
               'order_products': order_products, 'customer': customer}
    return render(request, 'store/adminPanel/customer_orders.html', context)


@admin_only
def subCategoryforms(request):
    sb_form = SubCategoryForm()
    category_form = CategoryForm()
    context = {'sb_form': sb_form, 'category_form': category_form}
    return render(request, 'store/adminPanel/add_category_subcategory.html', context)


@admin_only
def addCategory(request):
    form = CategoryForm()
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('create_category_subcategory')
    return redirect('admin_panel')


@admin_only
def addSubCategory(request):
    form = SubCategoryForm()
    if request.method == 'POST':
        form = SubCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('create_category_subcategory')
    return redirect('admin_panel')


@admin_only
def products(request):
    products = Product.objects.all()
    subcategories = SubCategory.objects.all()
    subcategory_filter = request.GET.get('subcategory_filter')
    if is_valid_queryparam(subcategory_filter):
        products = products.filter(subcategory__name=subcategory_filter)

    products = paginatorUtil(request, products)
    context = {'products': products, 'subcategories': subcategories,
               'subcategory_filter': subcategory_filter}
    return render(request, 'store/adminPanel/products.html', context)


@admin_only
def updateProduct(request, pk):
    product = Product.objects.get(pk=pk)
    form = ProductForm(instance=product)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('products_list')
    context = {'form': form}
    return render(request, 'store/adminPanel/create_product.html', context)


@admin_only
def deleteProduct(request, pk):
    product = Product.objects.get(pk=pk)
    product.delete()

    return redirect('products_list')


@admin_only
def finishOrder(request, pk):
    order = Order.objects.get(pk=pk)
    order.finished = True
    order.save()
    return redirect('unfinished_orders')


@admin_only
def unfinishOrder(request, pk):
    order = Order.objects.get(pk=pk)
    order.finished = False
    order.save()
    return redirect('finished_orders')


@admin_only
def showOrder(request, pk):
    order = Order.objects.get(pk=pk)
    # orderproducts = OrderProduct.objects.filter(order=order)
    orderproducts = order.orderproduct_set.all()

    context = {'order': order, 'orderproducts': orderproducts}
    return render(request, 'store/adminPanel/order.html', context)


@admin_only
def finishedOrders(request):
    data = adminPanelProducts(request)
    orders = data['orders']
    order_products = data['order_products']

    context = {'orders': orders,
               'order_products': order_products, }
    return render(request, 'store/adminPanel/finished_orders.html', context)


@admin_only
def deleteOrder(request, pk):
    order = Order.objects.get(pk=pk)
    order.delete()
    return redirect('admin_panel')
