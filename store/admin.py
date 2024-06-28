from django.contrib import admin
from .models import *
# Register your models here.

class StoreAdmin(admin.ModelAdmin):
    list_display = ('store_name', 'description', 'email')
class productAdmin(admin.ModelAdmin):
    list_display = ('name','category', 'store', 'price')
class CartAdmin(admin.ModelAdmin):
    list_display = ('user','product','quantity','size')
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user','email','date','telephone','delivered')
admin.site.register(Store, StoreAdmin)
admin.site.register(product, productAdmin)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(Category)