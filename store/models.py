from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
# Create your models here.
class Category(models.Model):
    cat_name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.cat_name

class Store(models.Model):
    store_name = models.CharField(max_length=100)
    description = models.TextField()
    email = models.EmailField(max_length=254, null=True, blank=True, default='')

    def __str__(self):
        return self.store_name

class product(models.Model):
    name = models.CharField(max_length=100, default='')
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True)
    store = models.ForeignKey('Store', on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    price = models.CharField(max_length=50, default='')
    description = models.TextField()


    def __str__(self):
        return self.name
    def summary(self):
        return self.description[:40]

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default='', null=True)
    product = models.ForeignKey(product,on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    size = models.CharField(max_length=10, default='')
    def __str__(self):
        return self.user.username

class Item(models.Model):
    stuff = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey('product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    size = models.CharField(max_length=10, default='')

    def __str__(self):
        return f"{self.quantity} x {self.product.name}({self.size}) by {self.product.store}"

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default='', null=True)
    name = models.CharField(max_length=100, default='')
    address = models.TextField(default='')
    items = models.ManyToManyField(Item)
    email = models.EmailField(max_length=254, null=True, blank=True, default='')
    telephone = models.CharField(max_length=14, default="")
    payment_status = models.BooleanField(default=False)
    delivered = models.BooleanField(default=False)
    date = models.DateTimeField(default=timezone.now())
    instructions = models.TextField()

    def __str__(self):
        return f"Order by {self.name}"

    def get_recipient_list(self):
        store_emails = set()
        for item in self.order_items.all():
            if item.product.store and item.product.store.email:
                store_emails.add(item.product.store.email)
        recipient_list = [self.email] + list(store_emails)
        return recipient_list
