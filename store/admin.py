from django.contrib import admin
from .models import *
# Register your models here.

class StoreAdmin(admin.ModelAdmin):
    list_display = ('store_name', 'description', 'email')
class productAdmin(admin.ModelAdmin):
    list_display = ('name','category', 'store', 'price', 'stock')
class CartAdmin(admin.ModelAdmin):
    list_display = ('user','product','quantity','size')
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user','name','email','date','telephone','delivered', 'payment_status')
    search_fields = ('name', 'email', 'telephone', 'address', 'instructions')
    def user_name(self, obj):
        return obj.user.username if obj.user else None
admin.site.register(Store, StoreAdmin)
admin.site.register(product, productAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Category)
# admin.site.register(Vendor)