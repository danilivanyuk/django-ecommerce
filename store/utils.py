from django.db.models import Count
from collections import deque
from datetime import datetime, timedelta
from dateutil.relativedelta import *
import json
from . models import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from functools import reduce
import operator
from django.db.models import Q


def is_valid_queryparam(param):
    return param != '' and param is not None


def filterProducts(request, products):
    title = request.GET.get('title_contains')
    sizes = request.GET.getlist('size')
    gender = request.GET.getlist('gender_select')
    print(gender)
    price_min = request.GET.get('price-from-filter')
    price_max = request.GET.get('price-to-filter')
    sort = request.GET.get('sort')

    if sizes != []:
        products = products.filter(
            reduce(lambda x, y: x | y, [Q(size__contains=item) for item in sizes]))
    if gender != []:
        products = products.filter(
            reduce(lambda x, y: x | y, [
                   Q(gender=item) for item in gender])
        )
    if is_valid_queryparam(sort):
        if sort == 'order_by_min_price':
            products = products.order_by('price')
        if sort == 'order_by_max_price':
            products = products.order_by('-price')
        if sort == 'new_arr':
            products = products.order_by('created_at')
    if is_valid_queryparam(title):
        if title != '':
            products = products.filter(title__contains=title)
    # if is_valid_queryparam(gender):
    #     products = products.filter(gender__contains=gender)
    if is_valid_queryparam(price_min):
        products = products.filter(price__gte=price_min)
    if is_valid_queryparam(price_max):
        products = products.filter(price__lt=price_max)
    return {'products': products, 'sizes': sizes, 'price_min': price_min, 'price_max': price_max, 'sort_value': sort, 'gender': gender}


def paginatorUtil(request, products):
    page = request.GET.get('page', 1)
    paginator = Paginator(products, 10)
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    return products


def cookieCart(request):
    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}
    items = []
    order = {'get_cart_total': 0, 'get_cart_items': 0}
    cartItems = order['get_cart_items']

    for i in cart:
        try:
            cartItems += cart[i]['quantity']
            product = Product.objects.get(id=i)
            total = (product.price * cart[i]["quantity"])

            order['get_cart_total'] += total
            order['get_cart_items'] += cart[i]["quantity"]

            item = {
                'product': {
                    'id': product.id,
                    'title': product.title,
                    'gender': product.gender,
                    'imageURL': product.imageURL,
                    'price': product.price,
                    'color': product.color,
                    'description': product.description,
                },
                'quantity': cart[i]['quantity'],
                'size': cart[i]['size'],
                'get_total': total
            }

            items.append(item)
        except:
            pass
    return {'cartItems': cartItems, 'order': order, 'items': items}


def cartData(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        # CREATE or get if EXIST order
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        # Get all orderitem child of ORDER
        items = order.orderproduct_set.all()
        cartItems = order.get_cart_items
    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        order = cookieData['order']
        items = cookieData['items']
    return {'cartItems': cartItems, 'order': order, 'items': items}


def guestOrder(request, data):
    name = data['form']['name']
    phone = data['form']['telephone']

    cookieData = cookieCart(request)
    items = cookieData['items']

    customer, created = Customer.objects.get_or_create(
        phone=phone,
    )
    customer.name = name
    customer.save()

    order = Order.objects.create(
        customer=customer,
        complete=False
    )
    for item in items:
        product = Product.objects.get(id=item['product']['id'])

        orderProduct = OrderProduct.objects.create(
            product=product,
            order=order,
            quantity=item['quantity'],
            size=item['size']
        )
    return customer, order

# ShippingAdress.objects.create(
#         customer=customer,
#         order=order,
#         city=data['shipping']['city'],
#         street=data['shipping']['street'],
#         house=data['shipping']['house'],
#         appartament=data['shipping']['appartament']
#     )


def adminPanelProducts(request):

    orders = Order.objects.all()
    order_products = OrderProduct.objects.filter(
        order__in=orders)

    unfinished_order = Order.objects.filter(
        finished=False, complete=True)
    unfinished_orders_count = len(Order.objects.filter(
        finished=False, complete=True))

    # shipping_adresses = ShippingAdress.objects.filter(order__in=orders)
    return {'orders': orders, 'order_products': order_products, 'unfinished_order': unfinished_order, 'unfinished_orders_count': unfinished_orders_count}


def adminPanelEarningsOverview(request):
    today = datetime.datetime.now()
    # Get next month and year using relativedelta
    # next_month = today + relativedelta(months=1)
    # How many months do you want to go back?

    num_months_back = 4

    i = 0
    deque_months = deque()
    deque_months_decimal = deque()

    while i <= num_months_back:
        curr_date = today + relativedelta(months=-i)
        deque_months.appendleft(curr_date.strftime('%b'))
        deque_months_decimal.appendleft(curr_date.strftime('%m'))

        i = i+1

    # Convert deque to list
    # print(list(deque_months))
    months = list(deque_months)
    months_decimal = list(deque_months_decimal)

    annual_orders = Order.objects.filter(
        ordered_date__year=today.strftime('%Y'))

    order_earnings_1 = Order.objects.filter(
        ordered_date__month=months_decimal[0])
    order_earnings_2 = Order.objects.filter(
        ordered_date__month=months_decimal[1])
    order_earnings_3 = Order.objects.filter(
        ordered_date__month=months_decimal[2])
    order_earnings_4 = Order.objects.filter(
        ordered_date__month=months_decimal[3])
    order_earnings_5 = Order.objects.filter(
        ordered_date__month=months_decimal[4])

    earnings_month_1, earnings_month_2, earnings_month_3, earnings_month_4, earnings_month_5, annual_earnings = 0, 0, 0, 0, 0, 0
    for i in order_earnings_1:
        earnings_month_1 += get_total_month_earning(i)

    for i in order_earnings_2:
        earnings_month_2 += get_total_month_earning(i)

    for i in order_earnings_3:
        earnings_month_3 += get_total_month_earning(i)

    for i in order_earnings_4:
        earnings_month_4 += get_total_month_earning(i)

    for i in order_earnings_5:
        earnings_month_5 += get_total_month_earning(i)
    for i in annual_orders:
        annual_earnings += get_total_month_earning(i)

    return {'months': months, 'earnings_month_1': earnings_month_1, 'earnings_month_2': earnings_month_2, 'earnings_month_3': earnings_month_3, 'earnings_month_4': earnings_month_4, 'earnings_month_5': earnings_month_5, 'annual_earnings': annual_earnings}


def get_total_month_earning(order_id):
    a = []
    orderproducts = OrderProduct.objects.filter(order=order_id)
    for i in orderproducts:
        if i.order.finished:
            a.append(i.product.price*i.quantity)
    earnings = sum(a)
    return earnings
