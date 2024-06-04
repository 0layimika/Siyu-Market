from django.contrib import admin
from django.urls import path, include
from . import views

# app_name = "store"
urlpatterns=[
    path('',views.home.as_view(), name="home"),
    path('entry/', views.entry.as_view(), name='entry'),
    path('perfume/',views.perfume_view,name="perfume"),
    path('jewelry/',views.jewelry_view,name='jewelry'),
    path('clothing/',views.clothing_view,name='clothing'),
    path('accessories/',views.accessories_view,name='accessories'),
    path('shop/<str:shop>', views.store_view, name='shop'),
    path('details/<int:product_id>',views.product_detail,name="details"),
    path('cart/<int:product_id>',views.add_to_cart,name="cart"),
    path('cart_item/',views.cart,name="cart_item"),
    path('remove/<int:cart_item_id>',views.cart_remove,name='remove'),
    path('checkout/',views.checkout,name='checkout'),
    path('update/<int:cart_item_id>',views.cart_update,name='update'),
    path('search/',views.search,name='search'),
    path('payment/callback',views.payment_callback, name='payment_callback'),

]