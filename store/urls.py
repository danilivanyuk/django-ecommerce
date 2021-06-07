from django.urls import path
from . import views

urlpatterns = [

    path('register/', views.registerPage, name="register"),
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutUser, name="logout"),

    path('', views.homepage, name="homepage"),
    path('profile/', views.userProfile, name="userProfile"),
    path('search_result/', views.search, name="search_result"),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('category/<int:category_id>/',
         views.category, name="category"),
    path('catalog/<int:subcategory_id>/',
         views.subcategory, name="subcategory"),
    path('catalog/product/<int:product_id>/',
         views.product, name="product"),

    # ADMIN PANEL

    path('admin_panel/', views.adminPanel, name="admin_panel"),
    path('admin_panel/create_product/',
         views.createProduct, name='create_product'),
    path('admin_panel/create_category_subcategory/',
         views.subCategoryforms, name='create_category_subcategory'),
    path('admin_panel/all_categories/',
         views.showAllCategories, name='all_categories'),
    path('admin_panel/add_category/',
         views.addCategory, name='add_category'),
    path('admin_panel/add_subcategory/',
         views.addSubCategory, name='add_subcategory'),
    path('admin_panel/delete_subcategory/<int:subcategory_id>',
         views.deleteSubCategory, name='delete_subcategory'),
    path('admin_panel/delete_category/<int:category_id>',
         views.deleteCategory, name='delete_category'),



    path('admin_panel/product_list/',
         views.products, name='products_list'),
    path('admin_panel/finish_order/<int:pk>',
         views.finishOrder, name="finish_order"),
    path('admin_panel/delete_order/<int:pk>',
         views.deleteOrder, name="delete_order"),

    path('admin_panel/product_list/update_product/<int:pk>',
         views.updateProduct, name='update_product'),
    path('admin_panel/product_list/delete_product/<int:pk>',
         views.deleteProduct, name='delete_product'),

    path('admin_panel/finished_orders/',
         views.finishedOrders, name="finished_orders"),
    path('admin_panel/order/<int:pk>', views.showOrder, name='show_order'),
    path('admin_panel/unfinished_orders',
         views.unfinishedOrders, name='unfinished_orders'),
    path('admin_panel/unfinish_order/<int:pk>',
         views.unfinishOrder, name="unfinish_order"),
    path('admin_panel/customers/',
         views.showCustomers, name="customers"),
    path('admin_panel/customer_orders/<int:customer_id>',
         views.showCustomerOrders, name="customer_orders"),

    # PROCESSES

    path('cancel_order/', views.cancelOrder, name='cancel_order'),
    path('update_item/', views.updateItem, name='update_item'),
    path('process_order/', views.processOrder, name='process_order'),
]
